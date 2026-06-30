"""Missions ETL — every 30 minutes."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.insert(0, "/opt/airflow/plugins")
from etl_utils import get_engines, upsert_dim_date, sync_dimensions
import pandas as pd
from sqlalchemy import text

default_args = {"owner": "tpvs", "retries": 2, "retry_delay": timedelta(minutes=5)}


def run_etl_missions():
    mysql_engine, pg_engine = get_engines()
    sync_dimensions(mysql_engine, pg_engine)
    df = pd.read_sql("""
        SELECT id, agent_id, station_id, date_debut, date_fin, statut, zone_couverture, duree_prevue_minutes
        FROM mission WHERE statut IN ('EN_COURS', 'TERMINEE', 'PLANIFIEE')
    """, mysql_engine)

    for _, row in df.iterrows():
        date_id = upsert_dim_date(pg_engine, row["date_debut"].date())
        duree = None
        taux = None
        if row["date_fin"] and row["date_debut"]:
            duree = (row["date_fin"] - row["date_debut"]).total_seconds() / 60
            taux = min(duree / max(row["duree_prevue_minutes"], 1), 1.0)
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.dim_mission (mission_id, zone_couverture, statut)
                VALUES (:id, :zone, :statut)
                ON CONFLICT (mission_id) DO UPDATE SET statut=:statut, updated_at=NOW()
            """), {"id": str(row["id"]), "zone": row["zone_couverture"], "statut": row["statut"]})
            conn.execute(text("""
                INSERT INTO dwh.fact_missions
                (mission_id, date_id, agent_id, station_id, duree_minutes, duree_prevue_minutes, taux_completion, statut, zone_couverture)
                VALUES (:mid, :did, :aid, :sid, :duree, :prevue, :taux, :statut, :zone)
            """), {
                "mid": str(row["id"]), "did": date_id, "aid": str(row["agent_id"]),
                "sid": str(row["station_id"]), "duree": duree, "prevue": row["duree_prevue_minutes"],
                "taux": taux, "statut": row["statut"], "zone": row["zone_couverture"],
            })
            conn.commit()


with DAG(
    dag_id="etl_missions",
    default_args=default_args,
    schedule_interval="*/30 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "missions"],
) as dag:
    PythonOperator(task_id="load_missions", python_callable=run_etl_missions)
