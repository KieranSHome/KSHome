CREATE TABLE IF NOT EXISTS blocks_sessions (id TEXT PRIMARY KEY, created INTEGER NOT NULL, rate_key TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS blocks_sessions_rate ON blocks_sessions(rate_key, created);
CREATE TABLE IF NOT EXISTS blocks_scores (id TEXT PRIMARY KEY, name TEXT NOT NULL, score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 10000000), lines INTEGER NOT NULL CHECK(lines BETWEEN 0 AND 10000), created INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS blocks_scores_rank ON blocks_scores(score DESC, created ASC);