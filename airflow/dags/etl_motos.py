"""Motos GPS ETL — every 15 minutes."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.insert(0, "/opt/airflow/plugins")
from etl_utils import get_engines, upsert_dim_date
import pandas as pd
from sqlalchemy import text

default_args = {"owner": "tpvs", "retries": 2, "retry_delay": timedelta(minutes=3)}


def run_etl_motos():
    mysql_engine, pg_engine = get_engines()
    df = pd.read_sql("""
        SELECT m.id, m.agent_assigne_id, m.kilometrage, m.niveau_batterie,
               m.latitude, m.longitude, m.statut_moto, m.position_timestamp
        FROM moto m
    """, mysql_engine)

    today_id = upsert_dim_date(pg_engine, datetime.now().date())
    for _, row in df.iterrows():
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.fact_motos
                (moto_id, date_id, agent_id, kilometrage, niveau_batterie, latitude, longitude, statut_moto)
                VALUES (:mid, :did, :aid, :km, :bat, :lat, :lng, :statut)
            """), {
                "mid": str(row["id"]), "did": today_id,
                "aid": str(row["agent_assigne_id"]) if row["agent_assigne_id"] else None,
                "km": float(row["kilometrage"]), "bat": row["niveau_batterie"],
                "lat": float(row["latitude"]), "lng": float(row["longitude"]),
                "statut": row["statut_moto"],
            })
            conn.commit()


with DAG(
    dag_id="etl_motos",
    default_args=default_args,
    schedule_interval="*/15 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "motos"],
) as dag:
    PythonOperator(task_id="load_motos", python_callable=run_etl_motos)
