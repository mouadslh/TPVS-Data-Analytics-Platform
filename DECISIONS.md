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
