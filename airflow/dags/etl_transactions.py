"""Hourly ETL — load validated transactions into fact_transactions."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.insert(0, "/opt/airflow/plugins")
from etl_utils import get_engines, get_watermark, set_watermark, sync_dimensions, upsert_dim_date
import pandas as pd
from sqlalchemy import text

default_args = {
    "owner": "tpvs",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


def run_etl_transactions():
    mysql_engine, pg_engine = get_engines()
    sync_dimensions(mysql_engine, pg_engine)
    watermark = get_watermark(pg_engine, "etl_transactions")

    df = pd.read_sql(f"""
        SELECT id, agent_id, station_id, machine_id, mission_id, montant,
               type_paiement, statut_validation, statut_sync, timestamp, numero_transaction, type_carte
        FROM transaction
        WHERE statut_validation = 'VALIDEE' AND timestamp > '{watermark}'
        ORDER BY timestamp
    """, mysql_engine)

    if df.empty:
        return

    max_ts = df["timestamp"].max()
    carte_map = {}
    with pg_engine.connect() as conn:
        rows = conn.execute(text("SELECT carte_type_id, type_carte FROM dwh.dim_carte")).fetchall()
        carte_map = {r[1]: r[0] for r in rows}

    for _, row in df.iterrows():
        date_id = upsert_dim_date(pg_engine, row["timestamp"].date())
        carte_id = carte_map.get(row["type_carte"])
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.fact_transactions
                (transaction_id, date_id, agent_id, station_id, machine_id, mission_id,
                 carte_type_id, montant, type_paiement, statut_validation, statut_sync, numero_transaction)
                VALUES (:tid, :did, :aid, :sid, :mid, :misid, :cid, :montant, :tp, :sv, :ss, :num)
                ON CONFLICT (transaction_id) DO NOTHING
            """), {
                "tid": str(row["id"]), "did": date_id,
                "aid": str(row["agent_id"]), "sid": str(row["station_id"]),
                "mid": str(row["machine_id"]), "misid": str(row["mission_id"]) if row["mission_id"] else None,
                "cid": carte_id, "montant": float(row["montant"]),
                "tp": row["type_paiement"], "sv": row["statut_validation"],
                "ss": row["statut_sync"], "num": row["numero_transaction"],
            })
            conn.commit()

    set_watermark(pg_engine, "etl_transactions", max_ts)


with DAG(
    dag_id="etl_transactions",
    default_args=default_args,
    schedule_interval="@hourly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "transactions"],
) as dag:
    PythonOperator(task_id="load_transactions", python_callable=run_etl_transactions)
