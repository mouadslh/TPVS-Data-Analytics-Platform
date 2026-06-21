# TPVS Data Analytics Platform

Centralized data analytics platform for TPVS field agents, missions, transactions, card stock, and moto GPS tracking.

## Phase 0 — Infrastructure (current)

This phase delivers a Docker Compose skeleton with all core services and health-check endpoints. Application logic (models, ETL, dashboard modules) begins in Phase 1.

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Git
- 8 GB RAM recommended for the full stack

### Quick Start

```bash
# 1. Clone and enter the project
cd pfa4e

# 2. Create environment file
cp .env.example .env

# 3. Start the entire stack
docker compose up --build -d

# 4. Wait for services to become healthy (~2 min on first boot)
docker compose ps
```

### Health Check Endpoints

| Service   | URL                              | Expected response        |
|-----------|----------------------------------|--------------------------|
| Backend   | http://localhost:8000/api/health/ | `{"status":"ok",...}`  |
| Frontend  | http://localhost:3000/health       | `{"status":"ok",...}`  |
| Nginx     | http://localhost/health            | `{"status":"ok",...}`  |
| Nginx TLS | https://localhost/api/health/      | Backend health (self-signed cert) |
| Airflow   | http://localhost:8080/health       | Airflow health page    |

### Service Ports

| Service            | Port  |
|--------------------|-------|
| Nginx (HTTP/HTTPS) | 80, 443 |
| Django backend     | 8000  |
| React frontend     | 3000  |
| Airflow webserver  | 8080  |
| MySQL              | 3306  |
| PostgreSQL         | 5432  |
| Redis              | 6379  |

### Airflow Access

- URL: http://localhost:8080
- Username / password: values from `.env` (`AIRFLOW_ADMIN_USERNAME` / `AIRFLOW_ADMIN_PASSWORD`)

### TLS (Local Development)

Nginx generates a self-signed certificate on first startup. Browsers will show a security warning — accept for local dev. For production, replace files in `nginx/certs/` with real certificates (see `DECISIONS.md` D-003).

### Running Tests Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
pytest
ruff check .
```

**Frontend:**
```bash
cd frontend
npm install
npm run lint
npm run test
npm run build
```

### Project Structure

```
├── backend/          Django REST Framework API
├── frontend/         React + TypeScript SPA
├── airflow/          Airflow DAGs and plugins
├── nginx/            TLS reverse proxy
├── scripts/          DB init scripts
├── docs/             Documentation (Phase 1+)
├── docker-compose.yml
├── DECISIONS.md      Engineering decisions log
└── .env.example
```

### Stopping the Stack

```bash
docker compose down        # stop containers
docker compose down -v     # stop + remove volumes (fresh DB)
```

## Build Phases

| Phase | Scope                                      | Status      |
|-------|--------------------------------------------|-------------|
| 0     | Infrastructure & health checks             | ✅ Complete |
| 1     | Operational models, DWH schema, seed data    | Pending     |
| 2     | ETL pipelines (Airflow)                    | Pending     |
| 3     | Analytics API, RBAC, JWT                   | Pending     |
| 4     | React dashboard (9 modules)                | Pending     |
| 5     | PDF/Excel reports                          | Pending     |
| 6     | Anomaly detection                          | Pending     |
| 7     | Tests, hardening, documentation            | Pending     |

## License

Proprietary — internal use.
