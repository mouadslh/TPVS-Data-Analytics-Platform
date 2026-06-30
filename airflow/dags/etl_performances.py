"""Daily agent performance KPIs — midnight."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.insert(0, "/opt/airflow/plugins")
from etl_utils import get_engines, upsert_dim_date
import pandas as pd
from sqlalchemy import text

default_args = {"owner": "tpvs", "retries": 2, "retry_delay": timedelta(minutes=10)}


def run_etl_performances():
    mysql_engine, pg_engine = get_engines()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    date_id = upsert_dim_date(pg_engine, yesterday)

    df = pd.read_sql(f"""
        SELECT agent_id,
               COUNT(*) as nb_tx,
               SUM(CASE WHEN statut_validation='VALIDEE' THEN montant ELSE 0 END) as montant,
               SUM(CASE WHEN statut_validation='VALIDEE' THEN 1 ELSE 0 END) as validees
        FROM transaction
        WHERE DATE(timestamp) = '{yesterday}'
        GROUP BY agent_id
    """, mysql_engine)

    for _, row in df.iterrows():
        taux = row["validees"] / max(row["nb_tx"], 1)
        score = float(row["montant"]) * 0.6 + row["nb_tx"] * 0.4
        with pg_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dwh.fact_performances
                (date_id, agent_id, nb_transactions, montant_total, taux_validation, score_performance)
                VALUES (:did, :aid, :nb, :montant, :taux, :score)
                ON CONFLICT (date_id, agent_id) DO UPDATE SET
                    nb_transactions=:nb, montant_total=:montant, taux_validation=:taux,
                    score_performance=:score, loaded_at=NOW()
            """), {
                "did": date_id, "aid": str(row["agent_id"]),
                "nb": int(row["nb_tx"]), "montant": float(row["montant"] or 0),
                "taux": taux, "score": score,
            })
            conn.commit()


with DAG(
    dag_id="etl_performances",
    default_args=default_args,
    schedule_interval="0 0 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "performances"],
) as dag:
    PythonOperator(task_id="compute_performances", python_callable=run_etl_performances)
