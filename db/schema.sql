-- Essential Words bot schema (PostgreSQL)

CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    name       TEXT,
    username   TEXT,
    tg_id      BIGINT UNIQUE NOT NULL,
    created_on TIMESTAMPTZ DEFAULT now(),
    last_use   TIMESTAMPTZ,
    lg         TEXT,
    status     SMALLINT DEFAULT 1,
    rank       INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS users_rank_idx ON users (status, rank DESC);

-- changelog posts (/update), "about" posts (/about_update), newsletters (/newsletter).
-- The bot does not store the text: it keeps the message_id of the post in the admin
-- group and copies it to users, so formatting and media survive untouched.
CREATE TABLE IF NOT EXISTS sets (
    id      SERIAL PRIMARY KEY,
    date    TIMESTAMPTZ DEFAULT now(),
    version TEXT,
    lg      TEXT NOT NULL,
    msg_id  BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS abouts (LIKE sets INCLUDING ALL);
CREATE TABLE IF NOT EXISTS space (LIKE sets INCLUDING ALL);

-- One table per book: 30 units x 20 words.
CREATE TABLE IF NOT EXISTS book1 (
    id   SERIAL PRIMARY KEY,
    unit SMALLINT NOT NULL,
    eng  TEXT NOT NULL,
    rus  TEXT,
    uzb  TEXT
);

CREATE TABLE IF NOT EXISTS book2 (LIKE book1 INCLUDING ALL);
CREATE TABLE IF NOT EXISTS book3 (LIKE book1 INCLUDING ALL);
CREATE TABLE IF NOT EXISTS book4 (LIKE book1 INCLUDING ALL);
CREATE TABLE IF NOT EXISTS book5 (LIKE book1 INCLUDING ALL);
CREATE TABLE IF NOT EXISTS book6 (LIKE book1 INCLUDING ALL);

CREATE INDEX IF NOT EXISTS book1_unit_idx ON book1 (unit);
CREATE INDEX IF NOT EXISTS book2_unit_idx ON book2 (unit);
CREATE INDEX IF NOT EXISTS book3_unit_idx ON book3 (unit);
CREATE INDEX IF NOT EXISTS book4_unit_idx ON book4 (unit);
CREATE INDEX IF NOT EXISTS book5_unit_idx ON book5 (unit);
CREATE INDEX IF NOT EXISTS book6_unit_idx ON book6 (unit);
