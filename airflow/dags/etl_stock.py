"""Stock ETL — 2x daily."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.insert(0, "/opt/airflow/plugins")
from etl_utils import get_engines, upsert_dim_date
import pandas as pd
from sqlalchemy import text

default_args = {"owner": "tpvs", "retries": 2, "retry_delay": timedelta(minutes=10)}


def run_etl_stock():
    mysql_engine, pg_engine = get_engines()
    df = pd.read_sql("""
        SELECT s.id, s.type_carte, s.station_id, s.quantite_actuelle, s.quantite_initiale,
               s.seuil_alerte, s.taux_defectueux, s.date_mise_a_jour
        FROM stock_carte s
    """, mysql_engine)

    today_id = upsert_dim_date(pg_engine, datetime.now().date())
    carte_map = {}
    with pg_engine.connect() as conn:
        rows = conn.execute(text("SELECT carte_type_id, type_carte FROM dwh.dim_carte")).fetchall()
        carte_map = {r[1]: r[0] for r in rows}

    for _, row in df.iterrows():
        rotation = (row["quantite_initiale"] - row["quantite_actuelle"]) / max(row["quantite_initiale"], 1)
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.fact_stock
                (date_id, station_id, carte_type_id, quantite_actuelle, quantite_initiale,
                 seuil_alerte, taux_defectueux, taux_rotation, alerte_seuil)
                VALUES (:did, :sid, :cid, :qa, :qi, :seuil, :def, :rot, :alert)
            """), {
                "did": today_id, "sid": str(row["station_id"]),
                "cid": carte_map.get(row["type_carte"]), "qa": row["quantite_actuelle"],
                "qi": row["quantite_initiale"], "seuil": row["seuil_alerte"],
                "def": float(row["taux_defectueux"]), "rot": rotation,
                "alert": row["quantite_actuelle"] < row["seuil_alerte"],
            })
            conn.commit()


with DAG(
    dag_id="etl_stock",
    default_args=default_args,
    schedule_interval="0 6,18 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "stock"],
) as dag:
    PythonOperator(task_id="load_stock", python_callable=run_etl_stock)
