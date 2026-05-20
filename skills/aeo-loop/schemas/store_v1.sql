-- aeo-loop SQLite schema v1
-- Source of truth. Migrations live in subsequent store_v2.sql, store_v3.sql, etc.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS properties (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    domain       TEXT NOT NULL UNIQUE,
    brand_name   TEXT,
    one_liner    TEXT,
    category     TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS competitors (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id  INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    domain       TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (property_id, name)
);

CREATE TABLE IF NOT EXISTS queries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id  INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    query_text   TEXT NOT NULL,
    query_type   TEXT NOT NULL CHECK (query_type IN ('aeo', 'seo', 'both')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    retired_at   TEXT,
    UNIQUE (property_id, query_text)
);

CREATE TABLE IF NOT EXISTS runs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id  INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    run_type     TEXT NOT NULL CHECK (run_type IN ('bootstrap', 'weekly', 'adhoc')),
    iso_week     TEXT,
    started_at   TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at  TEXT,
    status       TEXT NOT NULL DEFAULT 'running'
                  CHECK (status IN ('running', 'completed', 'failed', 'partial'))
);
CREATE INDEX IF NOT EXISTS idx_runs_property_week
    ON runs (property_id, iso_week);

CREATE TABLE IF NOT EXISTS citations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    property_id       INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    query_id          INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    llm_provider      TEXT NOT NULL,
    is_cited          INTEGER,   -- 1 = cited, 0 = not cited, NULL = not checked
    citation_context  TEXT,       -- snippet of response containing the citation
    response_excerpt  TEXT,       -- first 500 chars of model response for audit
    competitor_cited  TEXT,       -- comma-separated list of competitors cited
    checked_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_citations_lookup
    ON citations (property_id, query_id, llm_provider, checked_at DESC);

CREATE TABLE IF NOT EXISTS rankings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    property_id   INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    query_id      INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    source        TEXT NOT NULL CHECK (source IN ('gsc', 'webfetch', 'serpapi', 'dataforseo')),
    position      REAL,
    url           TEXT,
    impressions   INTEGER,
    clicks        INTEGER,
    checked_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_rankings_lookup
    ON rankings (property_id, query_id, source, checked_at DESC);

CREATE TABLE IF NOT EXISTS audit_findings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    property_id   INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    category      TEXT NOT NULL,           -- e.g. 'technical', 'content', 'schema', 'geo'
    severity      TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    finding_text  TEXT NOT NULL,
    page_url      TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_audit_lookup
    ON audit_findings (property_id, category, severity);

CREATE TABLE IF NOT EXISTS actions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id             INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    property_id        INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    action_type        TEXT NOT NULL,
        -- e.g. 'blog_post', 'reddit_thread', 'wikipedia_edit', 'schema_add',
        --      'outreach_email', 'social_post', 'page_optimize', 'internal_link'
    title              TEXT NOT NULL,
    description        TEXT,
    target_url         TEXT,
    draft_path         TEXT,                -- filesystem path to the draft on disk
    predicted_impact   REAL,                -- 0..1 score
    effort_minutes     INTEGER,
    score              REAL,                -- predicted_impact / max(effort_minutes, 1)
    status             TEXT NOT NULL DEFAULT 'pending'
                         CHECK (status IN ('pending', 'in_progress', 'done', 'skipped')),
    cited_on           TEXT,                -- comma-separated platforms where action led to citation
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_actions_status
    ON actions (property_id, status, score DESC);

CREATE TABLE IF NOT EXISTS discovered_queries (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    property_id    INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    query_text     TEXT NOT NULL,
    source         TEXT NOT NULL,           -- 'paa', 'reddit', 'quora', 'llm_suggested'
    surface_count  INTEGER NOT NULL DEFAULT 1,
    first_seen     TEXT NOT NULL DEFAULT (datetime('now')),
    promoted       INTEGER NOT NULL DEFAULT 0,  -- 1 if operator added to queries table
    UNIQUE (property_id, query_text, source)
);
CREATE INDEX IF NOT EXISTS idx_discovered_property
    ON discovered_queries (property_id, surface_count DESC);

INSERT OR IGNORE INTO schema_version (version) VALUES (1);
