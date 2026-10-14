-- Read-only checks to run BEFORE 001_types_and_post_language.sql.
-- Changes nothing; every row of output is something that decides whether the
-- migration will succeed or will quietly produce wrong data.
--
--   psql -d essential -f db/migrations/preflight.sql

\echo '=== 1. already migrated? (expect: no) ==='
SELECT CASE WHEN count(*) > 0 THEN 'YES - 001 was already applied, do not run it again'
            ELSE 'no - 001 has not been applied' END AS status
FROM information_schema.columns WHERE table_name = 'sets' AND column_name = 'lg';

\echo '=== 2. duplicate tg_id (BLOCKER: the UNIQUE constraint would fail) ==='
SELECT tg_id, count(*) AS rows FROM users GROUP BY tg_id HAVING count(*) > 1;

\echo '=== 3. tg_id that is not a number (BLOCKER: the cast to bigint would fail) ==='
SELECT count(*) AS bad_tg_id FROM users WHERE tg_id IS NOT NULL AND tg_id !~ '^[0-9]+$';

\echo '=== 4. users with no tg_id (they get deleted by the migration) ==='
SELECT count(*) AS will_be_deleted FROM users WHERE tg_id IS NULL;

\echo '=== 5. dates that do not match dd.mm.yy/HH:MM (they become NULL) ==='
SELECT 'created_on' AS column, count(*) AS unparsable FROM users
 WHERE created_on IS NOT NULL AND created_on !~ '^\d{2}\.\d{2}\.\d{2}/\d{2}:\d{2}$'
UNION ALL
SELECT 'last_use', count(*) FROM users
 WHERE last_use IS NOT NULL AND last_use !~ '^\d{2}\.\d{2}\.\d{2}/\d{2}:\d{2}$';

\echo '=== 6. post rows the migration deletes (free text instead of a message id) ==='
SELECT count(*) AS will_be_deleted FROM sets
 WHERE version_description IS NULL OR version_description !~ '^[0-9]+$';

\echo '=== 7. do the newest three posts form one complete triple? ==='
\echo '    (the language of old posts is recovered from their order, so the last'
\echo '     three rows of each table must be one en/ru/uz set of the same version)'
SELECT 'sets' AS table, version, count(*) AS rows_in_triple
  FROM (SELECT version FROM sets
         WHERE version_description ~ '^[0-9]+$' ORDER BY id DESC LIMIT 3) t
 GROUP BY version
UNION ALL
SELECT 'abouts', version, count(*)
  FROM (SELECT version FROM abouts ORDER BY id DESC LIMIT 3) t GROUP BY version
UNION ALL
SELECT 'space', version::text, count(*)
  FROM (SELECT version FROM (SELECT ver_id AS version FROM space ORDER BY id DESC LIMIT 3) x) t
 GROUP BY version;

\echo '=== 8. row counts, to compare against after the migration ==='
SELECT 'users' AS table, count(*) FROM users
UNION ALL SELECT 'sets', count(*) FROM sets
UNION ALL SELECT 'abouts', count(*) FROM abouts
UNION ALL SELECT 'space', count(*) FROM space;
