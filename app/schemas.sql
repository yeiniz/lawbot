CREATE TABLE IF NOT EXISTS cases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  jurisdiction TEXT NOT NULL,
  external_id TEXT UNIQUE,
  title TEXT, court TEXT, case_number TEXT,
  decision_date TEXT, outcome TEXT, url TEXT,
  cited_statutes TEXT, summary TEXT, body TEXT
);
CREATE TABLE IF NOT EXISTS statutes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  jurisdiction TEXT NOT NULL,
  law_id TEXT, law_name TEXT, article TEXT, url TEXT, body TEXT
);
CREATE TABLE IF NOT EXISTS embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ref_table TEXT NOT NULL, ref_id INTEGER NOT NULL,
  model TEXT NOT NULL, dim INTEGER NOT NULL, vector BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_embeddings_table_ref ON embeddings(ref_table, ref_id);
CREATE INDEX IF NOT EXISTS idx_cases_date ON cases(decision_date);
