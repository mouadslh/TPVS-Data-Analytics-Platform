"""Daily report generation DAG — 06:00."""
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os
sys.path.insert(0, "/opt/airflow/plugins")

default_args = {"owner": "tpvs", "retries": 2, "retry_delay": timedelta(minutes=15)}


def generate_daily_report():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from apps.accounts.models import User, UserRole
    from apps.operational.models import TypeRapport
    from apps.reports.generators import create_rapport, generate_report

    admin = User.objects.filter(role=UserRole.SUPER_ADMIN).first()
    if not admin:
        return
    yesterday = date.today() - timedelta(days=1)
    rapport = create_rapport(TypeRapport.QUOTIDIEN, admin, yesterday, date.today())
    generate_report(rapport, admin)


with DAG(
    dag_id="rapport_quotidien",
    default_args=default_args,
    schedule_interval="0 6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["reports", "quotidien"],
) as dag:
    PythonOperator(task_id="generate_daily_report", python_callable=generate_daily_report)
