-- Brings a database created by the first version of the bot up to db/schema.sql.
--
-- Two things change:
--   1. tg_id was varchar and the dates were varchar in 'dd.mm.yy/HH:MM' format.
--      Comparing a varchar tg_id against an int from Telegram silently never
--      matched, and counting registrations per day needed a LIKE on a text column.
--   2. sets/abouts/space identified the language of a post by its position among
--      the last three rows. The language is now a column.
--
-- Run against an existing database:  psql -d essential -f db/migrations/001_types_and_post_language.sql

BEGIN;

-- The source timestamps carry no timezone; they were written in the bot's own.

ALTER TABLE users ALTER COLUMN tg_id TYPE BIGINT USING tg_id::bigint;
ALTER TABLE users ALTER COLUMN created_on TYPE TIMESTAMPTZ
    USING (to_timestamp(created_on, 'DD.MM.YY/HH24:MI')::timestamp AT TIME ZONE 'Asia/Tashkent');
ALTER TABLE users ALTER COLUMN last_use TYPE TIMESTAMPTZ
    USING (to_timestamp(last_use, 'DD.MM.YY/HH24:MI')::timestamp AT TIME ZONE 'Asia/Tashkent');
ALTER TABLE users ALTER COLUMN created_on SET DEFAULT now();
ALTER TABLE users ALTER COLUMN status SET DEFAULT 1;
ALTER TABLE users ALTER COLUMN rank SET DEFAULT 0;
UPDATE users SET rank = 0 WHERE rank IS NULL;
UPDATE users SET status = 1 WHERE status IS NULL;

DELETE FROM users WHERE tg_id IS NULL;
ALTER TABLE users ALTER COLUMN tg_id SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT users_tg_id_key UNIQUE (tg_id);
CREATE INDEX IF NOT EXISTS users_rank_idx ON users (status, rank DESC);

-- sets: version_description held the message id, plus a couple of rows from the
-- very first tests that held free text and cannot become a message id.
DELETE FROM sets WHERE version_description IS NULL OR version_description !~ '^[0-9]+$';
ALTER TABLE sets RENAME COLUMN version_description TO msg_id;
ALTER TABLE sets ALTER COLUMN msg_id TYPE BIGINT USING msg_id::bigint;
ALTER TABLE sets ALTER COLUMN msg_id SET NOT NULL;
ALTER TABLE sets ADD COLUMN IF NOT EXISTS lg TEXT;

ALTER TABLE abouts RENAME COLUMN msg TO msg_id;
ALTER TABLE abouts ALTER COLUMN msg_id TYPE BIGINT USING msg_id::bigint;
ALTER TABLE abouts ALTER COLUMN msg_id SET NOT NULL;
ALTER TABLE abouts ADD COLUMN IF NOT EXISTS lg TEXT;

ALTER TABLE space RENAME COLUMN ver_id TO version;
ALTER TABLE space ALTER COLUMN version TYPE TEXT USING version::text;
ALTER TABLE space ALTER COLUMN msg_id TYPE BIGINT USING msg_id::bigint;
ALTER TABLE space ALTER COLUMN msg_id SET NOT NULL;
ALTER TABLE space ADD COLUMN IF NOT EXISTS lg TEXT;

-- Posts were always sent as en, ru, uz, so numbering backwards from the newest row
-- recovers the language of every existing triple.
UPDATE sets SET lg = v.lg FROM (
    SELECT id, CASE row_number() OVER (ORDER BY id DESC) % 3
                   WHEN 1 THEN 'uz' WHEN 2 THEN 'ru' ELSE 'en' END AS lg
    FROM sets) v WHERE sets.id = v.id;
UPDATE abouts SET lg = v.lg FROM (
    SELECT id, CASE row_number() OVER (ORDER BY id DESC) % 3
                   WHEN 1 THEN 'uz' WHEN 2 THEN 'ru' ELSE 'en' END AS lg
    FROM abouts) v WHERE abouts.id = v.id;
UPDATE space SET lg = v.lg FROM (
    SELECT id, CASE row_number() OVER (ORDER BY id DESC) % 3
                   WHEN 1 THEN 'uz' WHEN 2 THEN 'ru' ELSE 'en' END AS lg
    FROM space) v WHERE space.id = v.id;

ALTER TABLE sets ALTER COLUMN lg SET NOT NULL;
ALTER TABLE abouts ALTER COLUMN lg SET NOT NULL;
ALTER TABLE space ALTER COLUMN lg SET NOT NULL;

ALTER TABLE sets ALTER COLUMN date TYPE TIMESTAMPTZ
    USING (to_timestamp(date, 'DD.MM.YY/HH24:MI')::timestamp AT TIME ZONE 'Asia/Tashkent');
ALTER TABLE abouts ALTER COLUMN date TYPE TIMESTAMPTZ
    USING (to_timestamp(date, 'DD.MM.YY/HH24:MI')::timestamp AT TIME ZONE 'Asia/Tashkent');
ALTER TABLE space ALTER COLUMN date TYPE TIMESTAMPTZ
    USING (to_timestamp(date, 'DD.MM.YY/HH24:MI')::timestamp AT TIME ZONE 'Asia/Tashkent');
ALTER TABLE sets ALTER COLUMN date SET DEFAULT now();
ALTER TABLE abouts ALTER COLUMN date SET DEFAULT now();
ALTER TABLE space ALTER COLUMN date SET DEFAULT now();

-- the admin is configured through ADMIN_ID now
DROP TABLE IF EXISTS admins;

COMMIT;
