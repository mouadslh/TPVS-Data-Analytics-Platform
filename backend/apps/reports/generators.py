"""PDF and Excel report generation."""
import os
from datetime import date, timedelta
from pathlib import Path

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.analytics.services import kpis
from apps.operational.models import Rapport, StatutGeneration, TypeRapport

REPORTS_DIR = Path(os.environ.get("REPORTS_DIR", "/app/media/reports"))


def _ensure_dir():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_report(rapport: Rapport, user) -> str:
    """Generate PDF report and return file path."""
    rapport.statut_generation = StatutGeneration.EN_COURS
    rapport.save(update_fields=["statut_generation"])

    try:
        _ensure_dir()
        filename = f"{rapport.type_rapport}_{rapport.id}.pdf"
        filepath = REPORTS_DIR / filename

        if rapport.type_rapport == TypeRapport.QUOTIDIEN:
            data = _quotidien_data(user, rapport)
        elif rapport.type_rapport == TypeRapport.HEBDOMADAIRE:
            data = _hebdomadaire_data(user, rapport)
        elif rapport.type_rapport == TypeRapport.MENSUEL:
            data = _mensuel_data(user, rapport)
        elif rapport.type_rapport == TypeRapport.PERFORMANCE:
            data = {"agents": kpis.kpi_agent_performance(user, 3)}
        elif rapport.type_rapport == TypeRapport.STOCK:
            data = {"stock": kpis.kpi_stock_summary(user)}
        elif rapport.type_rapport == TypeRapport.TRANSACTION:
            data = {"summary": kpis.kpi_transactions_summary(user, rapport.periode_debut, rapport.periode_fin)}
        elif rapport.type_rapport == TypeRapport.STATION:
            data = {"stations": kpis.kpi_top_stations(user, 50)}
        else:
            data = {"banner": kpis.kpi_executive_banner(user)}

        rapport.donnees = data
        _write_pdf(filepath, rapport.type_rapport, data, rapport)
        _write_excel(REPORTS_DIR / f"{rapport.type_rapport}_{rapport.id}.xlsx", data)

        rapport.fichier_url = str(filepath)
        rapport.statut_generation = StatutGeneration.TERMINE
        rapport.date_generation = timezone.now()
        rapport.save()
        return str(filepath)
    except Exception as exc:
        rapport.statut_generation = StatutGeneration.ECHEC
        rapport.donnees = {"error": str(exc)}
        rapport.save()
        raise


def _quotidien_data(user, rapport):
    return {
        "banner": kpis.kpi_executive_banner(user),
        "transactions": kpis.kpi_transactions_summary(user, rapport.periode_debut, rapport.periode_fin),
        "missions": kpis.kpi_missions_summary(user),
    }


def _hebdomadaire_data(user, rapport):
    return {
        "banner": kpis.kpi_executive_banner(user),
        "top_agents": kpis.kpi_top_agents(user, 10),
        "n_vs_n1": kpis.kpi_n_vs_n1(user),
    }


def _mensuel_data(user, rapport):
    return {
        "monthly": kpis.kpi_monthly_evolution(user, 12),
        "agents": kpis.kpi_agent_performance(user, 1),
        "stock": kpis.kpi_stock_summary(user),
    }


def _write_pdf(filepath, report_type, data, rapport):
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Rapport TPVS — {report_type}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Période: {rapport.periode_debut} — {rapport.periode_fin}", styles["Normal"]),
        Spacer(1, 12),
    ]
    rows = [["Indicateur", "Valeur"]]
    if "banner" in data:
        for k, v in data["banner"].items():
            rows.append([k, str(v)])
    table = Table(rows, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(table)
    doc.build(story)


def _write_excel(filepath, data):
    wb = Workbook()
    ws = wb.active
    ws.title = "Rapport"
    ws.append(["Clé", "Valeur"])
    for section, content in data.items():
        ws.append([section, ""])
        if isinstance(content, dict):
            for k, v in content.items():
                ws.append([k, str(v)])
        elif isinstance(content, list):
            for item in content[:100]:
                ws.append([str(item.get("nom", item.get("agent_id", ""))), str(item)])
    ws["A1"].font = Font(bold=True)
    wb.save(str(filepath))
    return filepath


def create_rapport(type_rapport, user, periode_debut=None, periode_fin=None):
    if not periode_debut:
        periode_debut = date.today() - timedelta(days=1)
    if not periode_fin:
        periode_fin = date.today()
    return Rapport.objects.create(
        type_rapport=type_rapport,
        periode_debut=periode_debut,
        periode_fin=periode_fin,
        created_by=user,
    )
