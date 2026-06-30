# TPVS Data Analytics Platform

Centralized data analytics platform for TPVS field agents, missions, transactions, card stock, and moto GPS tracking.

## Quick Start

```bash
cp .env.example .env
docker compose up --build -d
# Wait ~3 min for migrations + seed data
docker compose ps
```

**Login:** https://localhost → `admin` / `changeme123`

## Architecture

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Ant Design + Recharts + Leaflet |
| Backend | Django REST Framework + JWT + RBAC |
| OLTP | MySQL 8 |
| OLAP | PostgreSQL 16 (star schema) |
| ETL | Apache Airflow 2.9 |
| Cache | Redis 7 |
| Proxy | Nginx (TLS) |

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard (TLS) | https://localhost | admin / changeme123 |
| API | http://localhost:8000/api/ | JWT |
| Swagger | http://localhost:8000/api/docs/ | — |
| Airflow | http://localhost:8080 | .env AIRFLOW_ADMIN_* |

## Seed Data

On first boot, the backend automatically runs:
```bash
python manage.py migrate
python manage.py init_dwh
python manage.py seed_data --agents 50 --days 180
```

Manual re-seed: `docker compose exec backend python manage.py seed_data --flush --agents 50 --days 180`

## Dashboard Modules

1. **Dashboard Exécutif** — KPIs, CA evolution, top agents/stations
2. **Analyse Transactions** — Filters, payment breakdown, heatmap, anomalies
3. **Performance Agents** — Ranking, radar chart, composite score
4. **Suivi Missions** — Completion rates, mission table
5. **Gestion Stock Cartes** — Levels, threshold alerts, rotation
6. **État Machines (TPVS)** — Fleet availability, battery alerts
7. **Suivi Motos & GPS** — Real-time Leaflet map
8. **Rapports & Exports** — PDF/Excel generation (7 types)
9. **Détection d'Anomalies** — 6-rule engine

## ETL Pipelines (Airflow)

| DAG | Schedule |
|-----|----------|
| etl_transactions | Hourly |
| etl_stock | 06:00, 18:00 daily |
| etl_missions | Every 30 min |
| etl_motos | Every 15 min |
| etl_performances | Daily 00:00 |
| rapport_quotidien | Daily 06:00 |

## RBAC Profiles

| Profile | Username | Scope |
|---------|----------|-------|
| Super Admin | admin | All |
| Admin Opérationnel | op.nord | Paris Nord zone |
| Admin Finance | finance | Financial data |
| Admin Technique | tech | Machines, motos, stock |

## Documentation

- [Data Dictionary](docs/data_dictionary.md)
- [ERD](docs/erd.mmd)
- [KPI Catalog](docs/kpi_catalog.md)
- [User Guide](docs/user_guide.md)
- [Engineering Decisions](DECISIONS.md)

## Production MySQL Migration

To connect real production MySQL, update only `.env` connection variables (`MYSQL_*`). No code changes required — see `DECISIONS.md` D-006.

## Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test && npm run build

# Lint
cd backend && ruff check .
cd frontend && npm run lint
```

## Build Phases

| Phase | Status |
|-------|--------|
| 0 — Infrastructure | ✅ |
| 1 — Models + DWH + Seed | ✅ |
| 2 — ETL Pipelines | ✅ |
| 3 — Analytics API + RBAC | ✅ |
| 4 — React Dashboard (9 modules) | ✅ |
| 5 — PDF/Excel Reports | ✅ |
| 6 — Anomaly Detection | ✅ |
| 7 — Tests + Docs | ✅ |
