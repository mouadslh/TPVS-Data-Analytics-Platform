# Engineering Decisions — TPVS Data Analytics Platform

This document records architectural and implementation decisions made where the master build prompt is silent on details.

## Phase 0 — Analysis & Setup

### D-001: Monorepo structure
**Decision:** Single repository with `backend/`, `frontend/`, `airflow/`, `nginx/`, and `docs/` directories.  
**Rationale:** Simplifies Docker Compose orchestration, CI, and cross-service development for a local-first platform.

### D-002: Airflow metadata database
**Decision:** Use the same PostgreSQL container with a separate database (`airflow_metadata`) for Airflow metadata, distinct from the DWH database (`tpvs_dwh`).  
**Rationale:** Reduces container count for local development while keeping OLAP and orchestration metadata isolated.

### D-003: TLS termination via Nginx
**Decision:** Nginx reverse proxy terminates TLS with self-signed certificates generated at container startup.  
**Rationale:** Matches production pattern (Section 10) while remaining zero-config for local dev. Real certificates can replace files in `nginx/certs/`.

### D-004: Django project layout
**Decision:** Django project named `config` with apps under `backend/apps/` (starting with `core` for health checks; domain apps added in Phase 1).  
**Rationale:** Standard Django layout scalable to multiple domain apps.

### D-005: React tooling
**Decision:** Vite + TypeScript + Ant Design (shell added in Phase 4; minimal placeholder in Phase 0).  
**Rationale:** Fixed stack per prompt; Vite provides fast HMR for development.

### D-006: Synthetic data → production MySQL migration path
**Decision:** All database access uses environment variables (`MYSQL_*`, `POSTGRES_*`). The `seed_data` management command (Phase 1) targets the operational MySQL instance. Switching to production requires only updating `.env` connection settings — no model or ETL code changes.  
**Rationale:** Explicit requirement in Section 0, Rule 4.

### D-007: Health check endpoints
**Decision:**
- Backend: `GET /api/health/` (JSON)
- Frontend (Nginx): `GET /health` (JSON)
- Airflow: built-in `/health` on webserver

**Rationale:** Enables Docker Compose `healthcheck` directives and Phase 0 verification.

### D-008: Custom User model (Phase 1)
**Decision:** Extended `AbstractUser` as `accounts.User` with UUID PK, matricule, role enum, and zone fields.  
**Rationale:** Single model covers agents and all 4 admin profiles per Section 6.

### D-009: DWH via SQL init + unmanaged Django models (Phase 1)
**Decision:** Star schema provisioned via `scripts/postgres/init-dwh.sql` and `manage.py init_dwh`; Django `apps.dwh` uses `managed=False` models for ORM read access.  
**Rationale:** Keeps OLAP schema independent from Django migrations while enabling test queries.

### D-010: ETL shared utilities in Airflow plugins (Phase 2)
**Decision:** `airflow/plugins/etl_utils.py` provides connection strings, date enrichment (French holidays via `holidays` lib), dimension sync, and watermark tracking.  
**Rationale:** DRY across 6 DAGs; idempotent incremental loads via `etl_watermarks` table.

### D-011: KPI layer in `apps.analytics.services.kpis` (Phase 3)
**Decision:** All KPIs computed as tested Python functions querying operational MySQL, with Redis cache (60s TTL) on API layer.  
**Rationale:** Single source of truth for KPI catalog; API views are thin wrappers.

### D-012: Report files on disk (Phase 5)
**Decision:** PDF (ReportLab) + Excel (openpyxl) written to `media/reports/` volume; `Rapport.fichier_url` stores path.  
**Rationale:** Simple local-first storage; production can swap to S3 via env config later.

### D-013: Anomaly engine as pure Python rules (Phase 6)
**Decision:** 6 rules in `apps.anomalies.engine.run_all_rules()` called synchronously from API; no separate message queue for local MVP.  
**Rationale:** Sufficient for local deployment; production can add Celery/Redis pub-sub later.
