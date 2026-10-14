# Deploying over the first version

The current code is not a drop-in replacement for the one running in production. Three
things change underneath it, and all three are handled by the order of the steps below.

## What breaks if you just swap the files

**1. The database schema.** `tg_id` becomes `BIGINT`, the dates become `TIMESTAMPTZ`, and
`sets`/`abouts`/`space` gain an `lg` column. The new code does not work against the old
schema, and the migration does not work against the new one. Run the migration while the
bot is stopped.

**2. Open dialogs in Redis.** The unit picker used to be started with `data=[book]` and
read it back as `start_data[0]`; it is now a dict read as `start_data['book']`. A user who
has the picker open when the bot restarts would hit
`TypeError: list indices must be integers or slices, not str`.

**3. Quizzes in flight.** The questions used to live in a module-level dict in the bot
process and now live in FSM storage. A user mid-quiz has no questions where the new code
looks for them, and gets "There are no words for the selected units yet" instead.

Both Redis problems disappear if the FSM keys are dropped during the restart. Everyone
mid-conversation starts over from `/start`, which is the cheapest acceptable outcome for
a one-off migration — no data is lost, coins and progress live in Postgres and Mongo.

## Requirements on the server

- **Python 3.10 or newer** — the code uses `int | None` annotations. Check with
  `python3 --version` before anything else.
- `pypdf` replaces `PyPDF2`, and the pinned versions are in `requirements.txt`.
- `data/book_units/` must stay where it is; it is gitignored, so a `git pull` leaves it
  alone, but a fresh clone into a new directory needs it copied over.
- The Google service-account key file, with its path in `GOOGLE_CREDENTIALS`.

## Order

```bash
# 0. check the Python version first; everything else is wasted if it is too old
python3 --version

# 1. stop the bot (systemd, screen, docker — whatever runs it)

# 2. back up both databases, this is the only way back
pg_dump -d essential > ~/essential-$(date +%F-%H%M).sql
mongodump --db essential --out ~/mongo-$(date +%F-%H%M)

# 3. read-only checks: fix anything they report before continuing
psql -d essential -f db/migrations/preflight.sql

# 4. migrate; it is one transaction, so a failure leaves the database untouched
psql -d essential -v ON_ERROR_STOP=1 -f db/migrations/001_types_and_post_language.sql

# 5. deploy the code and its dependencies
pip install -r requirements.txt

# 6. write .env — see .env.example. On the server MONGO_USER/MONGO_PASSWORD are set,
#    unlike a local instance that runs without auth.

# 7. drop the FSM keys, but nothing else that may share the Redis database
redis-cli -n 0 --scan --pattern 'fsm:*' | xargs -r -n 100 redis-cli -n 0 DEL

# 8. start the bot and watch the log
tail -f logs/bot.log
```

A healthy start logs three lines and nothing else:

```
INFO __main__: bot started
INFO aiogram.dispatcher: Start polling
INFO aiogram.dispatcher: Run polling for bot @... id=...
```

Then send `/start`, `/statistics` and `/version` to yourself, and play one quiz round.

## Rolling back

Stop the bot, restore the dump, put the old code back:

```bash
psql -d essential -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
psql -d essential < ~/essential-<timestamp>.sql
```

Mongo is only ever added to by this release (`ensure_balance` creates missing documents),
so it does not need restoring unless something else went wrong.

## Admin commands that no longer exist

`/admin`, `/admin_add4196`, `/test`, `/test2`, `/select`, `/select_mongo`, `/mongo`,
`/mongo_delete`, `/invite_add`, `/zero_coin`.

`/admin_add4196` let any user make themselves an admin, so it had to go; the admin is
`ADMIN_ID` in `.env` now and the `admins` table is dropped by the migration. `/mongo` and
`/invite_add` were one-off backfills — the bot creates what they created, when it needs it.
The rest were debug leftovers.

## One thing to know about production data

Until this release, a user with no balance document in Mongo was paid coins again on every
repeat of the same quiz, because the comparison that gates the payout had nothing to
compare against. `ensure_balance()` closes it, but balances already inflated that way stay
as they are. If the Top 10 has implausible numbers, that is where they came from.
