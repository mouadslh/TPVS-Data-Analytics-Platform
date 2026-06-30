"""KPI computation services — tested query layer for analytics API."""
from datetime import timedelta

import numpy as np
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import ExtractHour, TruncDate, TruncMonth
from django.utils import timezone

from apps.accounts.models import User, UserRole, UserStatut
from apps.core.permissions import get_user_zone
from apps.operational.models import (
    Machine,
    MachineStatut,
    Mission,
    MissionStatut,
    Moto,
    StatutMoto,
    StatutValidation,
    StockCarte,
    Transaction,
)


def _tx_qs(user, start=None, end=None):
    qs = Transaction.objects.select_related("agent", "station", "machine")
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(agent__zone_affectation=zone)
    elif user.role == UserRole.AGENT:
        qs = qs.filter(agent=user)
    if start:
        qs = qs.filter(timestamp__gte=start)
    if end:
        qs = qs.filter(timestamp__lte=end)
    return qs


def kpi_executive_banner(user):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tx_today = _tx_qs(user, start=today)
    validated = tx_today.filter(statut_validation=StatutValidation.VALIDEE)
    agents_qs = User.objects.filter(role=UserRole.AGENT, statut=UserStatut.ACTIF)
    zone = get_user_zone(user)
    if zone:
        agents_qs = agents_qs.filter(zone_affectation=zone)
    machines_qs = Machine.objects.filter(statut=MachineStatut.DISPONIBLE)
    if zone:
        machines_qs = machines_qs.filter(station__missions__agent__zone_affectation=zone).distinct()
    return {
        "ca_jour": float(validated.aggregate(t=Sum("montant"))["t"] or 0),
        "transactions_validees": validated.count(),
        "agents_actifs": agents_qs.count(),
        "machines_operationnelles": machines_qs.count(),
    }


def kpi_ca_evolution(user, days=30):
    start = timezone.now() - timedelta(days=days)
    qs = (
        _tx_qs(user, start=start)
        .filter(statut_validation=StatutValidation.VALIDEE)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(ca=Sum("montant"), volume=Count("id"))
        .order_by("day")
    )
    return [{"date": r["day"].isoformat(), "ca": float(r["ca"]), "volume": r["volume"]} for r in qs]


def kpi_top_agents(user, limit=5):
    qs = (
        _tx_qs(user)
        .filter(statut_validation=StatutValidation.VALIDEE)
        .values("agent__id", "agent__matricule", "agent__nom", "agent__prenom")
        .annotate(ca=Sum("montant"), volume=Count("id"))
        .order_by("-ca")[:limit]
    )
    return [
        {
            "agent_id": str(r["agent__id"]),
            "matricule": r["agent__matricule"],
            "nom": f"{r['agent__prenom']} {r['agent__nom']}",
            "ca": float(r["ca"]),
            "volume": r["volume"],
        }
        for r in qs
    ]


def kpi_top_stations(user, limit=5):
    qs = (
        _tx_qs(user)
        .filter(statut_validation=StatutValidation.VALIDEE)
        .values("station__id", "station__nom")
        .annotate(ca=Sum("montant"), volume=Count("id"))
        .order_by("-ca")[:limit]
    )
    return [
        {"station_id": str(r["station__id"]), "nom": r["station__nom"],
         "ca": float(r["ca"]), "volume": r["volume"]}
        for r in qs
    ]


def kpi_transactions_summary(user, start=None, end=None):
    qs = _tx_qs(user, start, end)
    total = qs.count()
    validated = qs.filter(statut_validation=StatutValidation.VALIDEE)
    rejected = qs.filter(statut_validation=StatutValidation.REJETEE)
    pending = qs.filter(statut_validation=StatutValidation.EN_ATTENTE)
    ca = validated.aggregate(t=Sum("montant"))["t"] or 0
    return {
        "ca_total": float(ca),
        "volume": total,
        "ticket_moyen": float(ca / validated.count()) if validated.count() else 0,
        "taux_validation": round(validated.count() / total, 4) if total else 0,
        "taux_rejet": round(rejected.count() / total, 4) if total else 0,
        "en_attente": pending.count(),
        "par_paiement": list(
            qs.values("type_paiement").annotate(count=Count("id"), ca=Sum("montant"))
        ),
    }


def kpi_agent_performance(user, months=3):
    start = timezone.now() - timedelta(days=months * 30)
    agents_qs = User.objects.filter(role=UserRole.AGENT)
    zone = get_user_zone(user)
    if zone:
        agents_qs = agents_qs.filter(zone_affectation=zone)

    results = []
    for agent in agents_qs:
        txs = Transaction.objects.filter(
            agent=agent, timestamp__gte=start, statut_validation=StatutValidation.VALIDEE,
        )
        missions = Mission.objects.filter(agent=agent, date_debut__gte=start)
        completed = missions.filter(statut=MissionStatut.TERMINEE).count()
        total_m = missions.count()
        ca = txs.aggregate(t=Sum("montant"))["t"] or 0
        vol = txs.count()
        score = float(ca) * 0.5 + vol * 0.3 + (completed / max(total_m, 1)) * 100 * 0.2
        results.append({
            "agent_id": str(agent.id),
            "matricule": agent.matricule,
            "nom": f"{agent.prenom} {agent.nom}",
            "zone": agent.zone_affectation,
            "ca": float(ca),
            "volume": vol,
            "missions_completees": completed,
            "taux_completion": round(completed / max(total_m, 1), 4),
            "score_performance": round(score, 2),
        })
    return sorted(results, key=lambda x: x["score_performance"], reverse=True)


def kpi_missions_summary(user):
    qs = Mission.objects.select_related("agent", "station")
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(agent__zone_affectation=zone)
    total = qs.count()
    completed = qs.filter(statut=MissionStatut.TERMINEE).count()
    cancelled = qs.filter(statut=MissionStatut.ANNULEE).count()
    in_progress = qs.filter(statut=MissionStatut.EN_COURS).count()
    durations = []
    for m in qs.filter(statut=MissionStatut.TERMINEE, date_fin__isnull=False):
        durations.append((m.date_fin - m.date_debut).total_seconds() / 60)
    return {
        "total": total,
        "terminees": completed,
        "en_cours": in_progress,
        "annulees": cancelled,
        "taux_completion": round(completed / total, 4) if total else 0,
        "taux_annulation": round(cancelled / total, 4) if total else 0,
        "duree_moyenne_minutes": round(sum(durations) / len(durations), 1) if durations else 0,
        "par_zone": list(
            qs.values("zone_couverture").annotate(
                total=Count("id"),
                completees=Count("id", filter=Q(statut=MissionStatut.TERMINEE)),
            )
        ),
    }


def kpi_stock_summary(user):
    qs = StockCarte.objects.select_related("station")
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(station__missions__agent__zone_affectation=zone).distinct()
    items = []
    for s in qs:
        items.append({
            "id": str(s.id),
            "type_carte": s.type_carte,
            "station": s.station.nom,
            "quantite_actuelle": s.quantite_actuelle,
            "seuil_alerte": s.seuil_alerte,
            "taux_defectueux": float(s.taux_defectueux),
            "alerte": s.quantite_actuelle < s.seuil_alerte,
            "taux_rotation": round(
                (s.quantite_initiale - s.quantite_actuelle) / max(s.quantite_initiale, 1), 4
            ),
        })
    return items


def kpi_machines_summary(user):
    qs = Machine.objects.select_related("station")
    total = qs.count()
    disponibles = qs.filter(statut=MachineStatut.DISPONIBLE).count()
    maintenance = qs.filter(statut=MachineStatut.EN_MAINTENANCE).count()
    low_battery = qs.filter(batterie__lt=20).count()
    return {
        "total": total,
        "disponibles": disponibles,
        "en_maintenance": maintenance,
        "taux_disponibilite": round(disponibles / total, 4) if total else 0,
        "batterie_moyenne": qs.aggregate(avg=Avg("batterie"))["avg"] or 0,
        "alertes_batterie": low_battery,
        "par_station": list(
            qs.values("station__nom", "station__id")
            .annotate(count=Count("id"), ca=Sum("transactions__montant"))
        ),
    }


def kpi_motos_summary(user):
    qs = Moto.objects.select_related("agent_assigne")
    return {
        "total": qs.count(),
        "disponibles": qs.filter(statut_moto=StatutMoto.DISPONIBLE).count(),
        "en_mission": qs.filter(statut_moto=StatutMoto.EN_MISSION).count(),
        "kilometrage_total": float(qs.aggregate(t=Sum("kilometrage"))["t"] or 0),
        "positions": [
            {
                "id": str(m.id),
                "type_moto": m.type_moto,
                "latitude": float(m.latitude),
                "longitude": float(m.longitude),
                "kilometrage": float(m.kilometrage),
                "niveau_batterie": m.niveau_batterie,
                "statut": m.statut_moto,
                "agent": m.agent_assigne.matricule if m.agent_assigne else None,
                "timestamp": m.position_timestamp.isoformat(),
            }
            for m in qs
        ],
    }


def kpi_hourly_heatmap(user, days=30):
    start = timezone.now() - timedelta(days=days)
    qs = (
        _tx_qs(user, start=start)
        .annotate(hour=ExtractHour("timestamp"))
        .values("hour")
        .annotate(count=Count("id"), ca=Sum("montant"))
        .order_by("hour")
    )
    return [{"hour": r["hour"], "count": r["count"], "ca": float(r["ca"] or 0)} for r in qs]


def kpi_n_vs_n1(user):
    now = timezone.now()
    current_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 1:
        prev_start = current_start.replace(year=now.year - 1, month=12)
    else:
        prev_start = current_start.replace(month=now.month - 1)
    current = _tx_qs(user, current_start, now).filter(statut_validation=StatutValidation.VALIDEE)
    previous = _tx_qs(user, prev_start, current_start).filter(statut_validation=StatutValidation.VALIDEE)
    ca_n = float(current.aggregate(t=Sum("montant"))["t"] or 0)
    ca_n1 = float(previous.aggregate(t=Sum("montant"))["t"] or 0)
    variation = round((ca_n - ca_n1) / ca_n1 * 100, 2) if ca_n1 else 0
    return {"ca_n": ca_n, "ca_n1": ca_n1, "variation_pct": variation}


def detect_transaction_anomalies(user, days=90):
    """Z-score anomaly flagging on transaction amounts."""
    start = timezone.now() - timedelta(days=days)
    qs = _tx_qs(user, start=start).filter(statut_validation=StatutValidation.VALIDEE)
    amounts = list(qs.values_list("montant", flat=True))
    if len(amounts) < 10:
        return []
    mean = float(np.mean(amounts))
    std = float(np.std(amounts))
    if std == 0:
        return []
    anomalies = []
    for tx in qs.order_by("-timestamp")[:500]:
        z = (float(tx.montant) - mean) / std
        if abs(z) > 3:
            anomalies.append({
                "transaction_id": str(tx.id),
                "numero": tx.numero_transaction,
                "montant": float(tx.montant),
                "z_score": round(z, 2),
                "agent": tx.agent.matricule,
                "timestamp": tx.timestamp.isoformat(),
            })
    return anomalies


def kpi_monthly_evolution(user, months=12):
    start = timezone.now() - timedelta(days=months * 30)
    qs = (
        _tx_qs(user, start=start)
        .filter(statut_validation=StatutValidation.VALIDEE)
        .annotate(month=TruncMonth("timestamp"))
        .values("month")
        .annotate(ca=Sum("montant"), volume=Count("id"))
        .order_by("month")
    )
    return [{"month": r["month"].strftime("%Y-%m"), "ca": float(r["ca"]), "volume": r["volume"]} for r in qs]
