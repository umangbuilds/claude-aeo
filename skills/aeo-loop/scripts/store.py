"""SQLite store for aeo-loop.

Single class wrapping sqlite3. Schema lives in schemas/store_v1.sql alongside
this file's parent directory. Future migrations go to store_v2.sql etc.; the
class auto-applies any version newer than what's recorded in schema_version.

Path defaults to ~/.local/share/aeo-loop/store.db. Override with the
AEO_LOOP_DB environment variable, or pass db_path explicitly to Store().
"""

from __future__ import annotations

import datetime as _dt
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_DB_DIR = Path.home() / ".local" / "share" / "aeo-loop"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "store.db"

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

_ALLOWED_MIGRATION_TABLES: frozenset = frozenset({"properties", "queries", "actions"})


def iso_week_now(now: Optional[_dt.datetime] = None) -> str:
    """Return ISO-week string like '2026-W20' for sortable storage."""
    when = now or _dt.datetime.now(_dt.timezone.utc)
    iso_year, iso_week, _ = when.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _resolve_db_path(db_path: Optional[str]) -> Path:
    if db_path:
        return Path(db_path).expanduser()
    env = os.environ.get("AEO_LOOP_DB")
    if env:
        return Path(env).expanduser()
    return DEFAULT_DB_PATH


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}


class Store:
    """Thin sqlite3 wrapper. One connection per Store instance.

    Methods are intentionally narrow — they cover the v0.1 use case and leave
    ad-hoc reporting to direct SQL via the .conn handle.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.path = _resolve_db_path(db_path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.apply_schema()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # --- schema / migration ---------------------------------------------------

    def current_schema_version(self) -> int:
        try:
            row = self.conn.execute(
                "SELECT MAX(version) AS v FROM schema_version"
            ).fetchone()
            return row["v"] or 0
        except sqlite3.OperationalError:
            return 0

    LATEST_SCHEMA_VERSION = 2

    def _column_exists(self, table: str, column: str) -> bool:
        rows = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(r["name"] == column for r in rows)

    def _ensure_column(self, table: str, column: str, type_and_constraints: str) -> None:
        """ALTER TABLE ADD COLUMN, guarded by table_info() check.

        SQLite ALTER TABLE is not idempotent — re-running raises "duplicate
        column". This guard makes the v2 migration safe to re-run from a
        partially-migrated DB.
        """
        if table not in _ALLOWED_MIGRATION_TABLES:
            raise ValueError(
                f"_ensure_column: table {table!r} not in allowlist "
                f"{sorted(_ALLOWED_MIGRATION_TABLES)}"
            )
        if not self._column_exists(table, column):
            self.conn.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {type_and_constraints}"
            )

    def apply_schema(self, schema_dir: Optional[Path] = None) -> None:
        """Apply every migration newer than the current schema_version.

        v1 is sourced from schemas/store_v1.sql (pure CREATE TABLE — safe to
        re-execute). v2 is driven inline with column-existence guards because
        ALTER TABLE ADD COLUMN is not idempotent in SQLite.
        """
        cur_version = self.current_schema_version()
        if cur_version >= self.LATEST_SCHEMA_VERSION:
            return  # nothing to do — short-circuit avoids per-call glob/stat

        directory = schema_dir or SCHEMAS_DIR
        if not directory.exists():
            raise FileNotFoundError(
                f"schema directory not found: {directory}. Re-install the skill."
            )

        if cur_version < 1:
            with open(directory / "store_v1.sql") as f:
                self.conn.executescript(f.read())

        if cur_version < 2:
            self._ensure_column("properties", "region", "TEXT NOT NULL DEFAULT 'global'")
            self._ensure_column("properties", "currency", "TEXT NOT NULL DEFAULT 'USD'")
            self._ensure_column("queries", "region", "TEXT")
            self._ensure_column("actions", "platform_region",
                                "TEXT NOT NULL DEFAULT 'global'")
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_properties_region ON properties (region)"
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_actions_platform_region "
                "ON actions (property_id, platform_region)"
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO schema_version (version) VALUES (2)"
            )

        self.conn.commit()

    # --- properties -----------------------------------------------------------

    def add_property(
        self,
        domain: str,
        brand_name: Optional[str] = None,
        one_liner: Optional[str] = None,
        category: Optional[str] = None,
        region: Optional[str] = None,
        currency: Optional[str] = None,
    ) -> int:
        """Insert or update a property. Idempotent on domain.

        region defaults to 'global'. Set 'india' to enable Indian-context
        geo-pinning of LLM citation prompts and prioritisation of Indian
        platforms in the action list.

        currency is an ISO 4217 code; defaults 'USD'. When region='india' and
        currency is unset, defaults to 'INR' — shared default for CLI and
        programmatic callers.
        """
        if currency is None and (region or "").lower() == "india":
            currency = "INR"
        cur = self.conn.execute(
            """
            INSERT INTO properties (domain, brand_name, one_liner, category, region, currency)
            VALUES (?, ?, ?, ?, COALESCE(?, 'global'), COALESCE(?, 'USD'))
            ON CONFLICT(domain) DO UPDATE SET
                brand_name = COALESCE(excluded.brand_name, brand_name),
                one_liner  = COALESCE(excluded.one_liner, one_liner),
                category   = COALESCE(excluded.category, category),
                region     = COALESCE(?, region),
                currency   = COALESCE(?, currency)
            RETURNING id
            """,
            (domain, brand_name, one_liner, category, region, currency, region, currency),
        )
        row = cur.fetchone()
        self.conn.commit()
        return row["id"]

    def get_property_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM properties WHERE domain = ?", (domain,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def list_properties(self) -> List[Dict[str, Any]]:
        return [
            _row_to_dict(r)
            for r in self.conn.execute("SELECT * FROM properties ORDER BY domain")
        ]

    # --- competitors / queries ------------------------------------------------

    def add_competitor(self, property_id: int, name: str, domain: Optional[str] = None) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO competitors (property_id, name, domain)
            VALUES (?, ?, ?)
            ON CONFLICT(property_id, name) DO UPDATE SET
                domain = COALESCE(excluded.domain, domain)
            RETURNING id
            """,
            (property_id, name, domain),
        )
        row = cur.fetchone()
        self.conn.commit()
        return row["id"]

    def add_query(
        self,
        property_id: int,
        query_text: str,
        query_type: str = "aeo",
        region: Optional[str] = None,
    ) -> int:
        if query_type not in ("aeo", "seo", "both"):
            raise ValueError(f"query_type must be aeo|seo|both, got {query_type!r}")
        cur = self.conn.execute(
            """
            INSERT INTO queries (property_id, query_text, query_type, region)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(property_id, query_text) DO UPDATE SET
                query_type = excluded.query_type,
                region     = COALESCE(excluded.region, queries.region),
                retired_at = NULL
            RETURNING id
            """,
            (property_id, query_text, query_type, region),
        )
        row = cur.fetchone()
        self.conn.commit()
        return row["id"]

    def list_queries(
        self, property_id: int, include_retired: bool = False
    ) -> List[Dict[str, Any]]:
        if include_retired:
            rows = self.conn.execute(
                "SELECT * FROM queries WHERE property_id = ? ORDER BY id",
                (property_id,),
            )
        else:
            rows = self.conn.execute(
                "SELECT * FROM queries WHERE property_id = ? AND retired_at IS NULL ORDER BY id",
                (property_id,),
            )
        return [_row_to_dict(r) for r in rows]

    def retire_query(self, query_id: int) -> None:
        self.conn.execute(
            "UPDATE queries SET retired_at = datetime('now') WHERE id = ?", (query_id,)
        )
        self.conn.commit()

    # --- runs -----------------------------------------------------------------

    def start_run(
        self,
        property_id: Optional[int],
        run_type: str,
        iso_week: Optional[str] = None,
    ) -> int:
        if run_type not in ("bootstrap", "weekly", "adhoc"):
            raise ValueError(f"run_type must be bootstrap|weekly|adhoc, got {run_type!r}")
        week = iso_week or iso_week_now()
        cur = self.conn.execute(
            """
            INSERT INTO runs (property_id, run_type, iso_week)
            VALUES (?, ?, ?)
            RETURNING id
            """,
            (property_id, run_type, week),
        )
        row = cur.fetchone()
        self.conn.commit()
        return row["id"]

    def finish_run(self, run_id: int, status: str = "completed") -> None:
        if status not in ("running", "completed", "failed", "partial"):
            raise ValueError(f"invalid run status {status!r}")
        self.conn.execute(
            "UPDATE runs SET status = ?, finished_at = datetime('now') WHERE id = ?",
            (status, run_id),
        )
        self.conn.commit()

    def latest_run(
        self, property_id: int, run_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if run_type:
            row = self.conn.execute(
                """
                SELECT * FROM runs
                WHERE property_id = ? AND run_type = ?
                ORDER BY started_at DESC LIMIT 1
                """,
                (property_id, run_type),
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT * FROM runs WHERE property_id = ? ORDER BY started_at DESC LIMIT 1",
                (property_id,),
            ).fetchone()
        return _row_to_dict(row) if row else None

    # --- citations ------------------------------------------------------------

    def record_citation(
        self,
        run_id: int,
        property_id: int,
        query_id: int,
        llm_provider: str,
        is_cited: Optional[int],
        citation_context: Optional[str] = None,
        response_excerpt: Optional[str] = None,
        competitor_cited: Optional[str] = None,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO citations
                (run_id, property_id, query_id, llm_provider, is_cited,
                 citation_context, response_excerpt, competitor_cited)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id, property_id, query_id, llm_provider, is_cited,
                citation_context, response_excerpt, competitor_cited,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def latest_citation_grid(self, property_id: int) -> Dict[tuple, Dict[str, Any]]:
        """Return {(query_id, llm_provider): citation_row} for the most recent
        citation per (query, provider) pair. NULL is_cited treated as not_checked.
        """
        rows = self.conn.execute(
            """
            SELECT c.* FROM citations c
            JOIN (
                SELECT query_id, llm_provider, MAX(checked_at) AS latest
                FROM citations WHERE property_id = ?
                GROUP BY query_id, llm_provider
            ) latest_per
            ON c.query_id = latest_per.query_id
               AND c.llm_provider = latest_per.llm_provider
               AND c.checked_at = latest_per.latest
            WHERE c.property_id = ?
            """,
            (property_id, property_id),
        )
        return {(r["query_id"], r["llm_provider"]): _row_to_dict(r) for r in rows}

    def citation_grid_for_week(
        self, property_id: int, iso_week: str
    ) -> Dict[tuple, Dict[str, Any]]:
        """Return {(query_id, llm_provider): citation_row} for runs in a given week."""
        rows = self.conn.execute(
            """
            SELECT c.* FROM citations c
            JOIN runs r ON c.run_id = r.id
            WHERE c.property_id = ? AND r.iso_week = ?
            """,
            (property_id, iso_week),
        )
        out: Dict[tuple, Dict[str, Any]] = {}
        for r in rows:
            out[(r["query_id"], r["llm_provider"])] = _row_to_dict(r)
        return out

    def citation_rate(self, property_id: int, iso_week: Optional[str] = None) -> float:
        """Return fraction of cited cells over checked cells (NULL excluded)."""
        if iso_week:
            grid = self.citation_grid_for_week(property_id, iso_week)
        else:
            grid = self.latest_citation_grid(property_id)
        checked = [r for r in grid.values() if r["is_cited"] is not None]
        if not checked:
            return 0.0
        cited = sum(1 for r in checked if r["is_cited"] == 1)
        return cited / len(checked)

    # --- rankings -------------------------------------------------------------

    def record_ranking(
        self,
        run_id: int,
        property_id: int,
        query_id: int,
        source: str,
        position: Optional[float],
        url: Optional[str] = None,
        impressions: Optional[int] = None,
        clicks: Optional[int] = None,
    ) -> int:
        if source not in ("gsc", "webfetch", "serpapi", "dataforseo"):
            raise ValueError(f"invalid ranking source {source!r}")
        cur = self.conn.execute(
            """
            INSERT INTO rankings
                (run_id, property_id, query_id, source, position, url, impressions, clicks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, property_id, query_id, source, position, url, impressions, clicks),
        )
        self.conn.commit()
        return cur.lastrowid

    # --- audit findings -------------------------------------------------------

    def record_audit_finding(
        self,
        run_id: int,
        property_id: int,
        category: str,
        severity: str,
        finding_text: str,
        page_url: Optional[str] = None,
    ) -> int:
        if severity not in ("critical", "high", "medium", "low", "info"):
            raise ValueError(f"invalid severity {severity!r}")
        cur = self.conn.execute(
            """
            INSERT INTO audit_findings
                (run_id, property_id, category, severity, finding_text, page_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_id, property_id, category, severity, finding_text, page_url),
        )
        self.conn.commit()
        return cur.lastrowid

    # --- actions --------------------------------------------------------------

    def add_action(
        self,
        run_id: int,
        property_id: int,
        action_type: str,
        title: str,
        description: Optional[str] = None,
        target_url: Optional[str] = None,
        draft_path: Optional[str] = None,
        predicted_impact: Optional[float] = None,
        effort_minutes: Optional[int] = None,
        platform_region: Optional[str] = None,
    ) -> int:
        score = None
        if predicted_impact is not None and effort_minutes:
            score = predicted_impact / max(effort_minutes, 1)
        cur = self.conn.execute(
            """
            INSERT INTO actions
                (run_id, property_id, action_type, title, description, target_url,
                 draft_path, predicted_impact, effort_minutes, score, platform_region)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, 'global'))
            """,
            (
                run_id, property_id, action_type, title, description, target_url,
                draft_path, predicted_impact, effort_minutes, score, platform_region,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_action_status(
        self, action_id: int, status: str, cited_on: Optional[str] = None
    ) -> None:
        if status not in ("pending", "in_progress", "done", "skipped"):
            raise ValueError(f"invalid action status {status!r}")
        self.conn.execute(
            """
            UPDATE actions
            SET status = ?, cited_on = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (status, cited_on, action_id),
        )
        self.conn.commit()

    def list_actions(
        self,
        property_id: int,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM actions WHERE property_id = ?"
        params: list = [property_id]
        if status:
            sql += " AND status = ?"
            params.append(status)
        sql += " ORDER BY score DESC NULLS LAST, created_at DESC"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        return [_row_to_dict(r) for r in self.conn.execute(sql, tuple(params))]

    # --- discovered queries ---------------------------------------------------

    def add_discovered_query(
        self,
        run_id: int,
        property_id: int,
        query_text: str,
        source: str,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO discovered_queries (run_id, property_id, query_text, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(property_id, query_text, source) DO UPDATE SET
                surface_count = surface_count + 1
            RETURNING id
            """,
            (run_id, property_id, query_text, source),
        )
        row = cur.fetchone()
        self.conn.commit()
        return row["id"]


if __name__ == "__main__":
    s = Store()
    s.apply_schema()
    print(f"Store at {s.path}, schema version {s.current_schema_version()}")
    s.close()
