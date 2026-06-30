"""Shared ETL utilities for Airflow DAGs."""
import logging
import os
from datetime import date, datetime

import holidays
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

MYSQL_URL = (
    f"mysql+mysqldb://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}"
    f"@{os.environ.get('MYSQL_HOST', 'mysql')}:{os.environ.get('MYSQL_PORT', '3306')}"
    f"/{os.environ.get('MYSQL_DATABASE', 'tpvs_operational')}"
)
PG_URL = (
    f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}"
    f"@{os.environ.get('POSTGRES_HOST', 'postgres')}:{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ.get('POSTGRES_DB', 'tpvs_dwh')}"
)

fr_holidays = holidays.France()


def get_engines():
    return create_engine(MYSQL_URL), create_engine(PG_URL)


def enrich_date_row(d: date) -> dict:
    return {
        "date": d,
        "jour": d.day,
        "semaine": d.isocalendar()[1],
        "mois": d.month,
        "trimestre": (d.month - 1) // 3 + 1,
        "annee": d.year,
        "jour_semaine": d.isoweekday(),
        "est_ferie": d in fr_holidays,
    }


def upsert_dim_date(pg_engine, dt: date) -> int:
    row = enrich_date_row(dt)
    with pg_engine.connect() as conn:
        result = conn.execute(
            text("SELECT date_id FROM dwh.dim_date WHERE date = :d"), {"d": dt}
        ).fetchone()
        if result:
            return result[0]
        result = conn.execute(
            text("""
                INSERT INTO dwh.dim_date (date, jour, semaine, mois, trimestre, annee, jour_semaine, est_ferie)
                VALUES (:date, :jour, :semaine, :mois, :trimestre, :annee, :jour_semaine, :est_ferie)
                RETURNING date_id
            """),
            row,
        )
        conn.commit()
        return result.fetchone()[0]


def get_watermark(pg_engine, pipeline: str):
    with pg_engine.connect() as conn:
        row = conn.execute(
            text("SELECT last_loaded_at FROM dwh.etl_watermarks WHERE pipeline_name = :p"),
            {"p": pipeline},
        ).fetchone()
        return row[0] if row else datetime(2020, 1, 1)


def set_watermark(pg_engine, pipeline: str, ts: datetime):
    with pg_engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO dwh.etl_watermarks (pipeline_name, last_loaded_at, updated_at)
                VALUES (:p, :ts, NOW())
                ON CONFLICT (pipeline_name) DO UPDATE SET last_loaded_at = :ts, updated_at = NOW()
            """),
            {"p": pipeline, "ts": ts},
        )
        conn.commit()


def sync_dimensions(mysql_engine, pg_engine):
    """Sync agent, station, machine, mission dimensions."""
    agents = pd.read_sql("SELECT id, matricule, nom, prenom, zone_affectation, niveau_accreditation, statut FROM utilisateur WHERE role='AGENT'", mysql_engine)
    for _, r in agents.iterrows():
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.dim_agent (agent_id, matricule, nom, prenom, zone_affectation, niveau_accreditation, statut)
                VALUES (:id, :mat, :nom, :prenom, :zone, :niv, :statut)
                ON CONFLICT (agent_id) DO UPDATE SET matricule=:mat, nom=:nom, prenom=:prenom,
                    zone_affectation=:zone, niveau_accreditation=:niv, statut=:statut, updated_at=NOW()
            """), {"id": str(r["id"]), "mat": r["matricule"], "nom": r["nom"], "prenom": r["prenom"],
                   "zone": r["zone_affectation"], "niv": r["niveau_accreditation"], "statut": r["statut"]})
            conn.commit()

    stations = pd.read_sql("SELECT id, nom, type_station, latitude, longitude, statut, lignes_desservies FROM station", mysql_engine)
    for _, r in stations.iterrows():
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.dim_station (station_id, nom, type_station, coords_gps, statut, lignes_desservies)
                VALUES (:id, :nom, :type, :gps, :statut, :lignes)
                ON CONFLICT (station_id) DO UPDATE SET nom=:nom, type_station=:type, statut=:statut, updated_at=NOW()
            """), {"id": str(r["id"]), "nom": r["nom"], "type": r["type_station"],
                   "gps": f"{r['latitude']},{r['longitude']}", "statut": r["statut"],
                   "lignes": str(r["lignes_desservies"])})
            conn.commit()
