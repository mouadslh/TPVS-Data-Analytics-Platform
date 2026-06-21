-- Phase 0: DWH schema placeholder
-- Full star schema is provisioned in Phase 1 via backend/dwh migrations.

CREATE SCHEMA IF NOT EXISTS dwh;
COMMENT ON SCHEMA dwh IS 'TPVS Data Warehouse — star schema (Phase 1+)';
