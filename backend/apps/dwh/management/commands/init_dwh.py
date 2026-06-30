from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Initialize the PostgreSQL DWH star schema"

    def handle(self, *args, **options):
        sql_path = Path(__file__).resolve().parents[5] / "scripts" / "postgres" / "init-dwh.sql"
        if not sql_path.exists():
            sql_path = Path("/app/scripts/postgres/init-dwh.sql")

        sql = sql_path.read_text()
        statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
        with connections["dwh"].cursor() as cursor:
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as exc:
                    if "already exists" not in str(exc).lower():
                        self.stderr.write(f"Warning: {exc}")
        self.stdout.write(self.style.SUCCESS("DWH star schema initialized."))
