"""Anomaly detection rule engine — 6 rules per spec."""
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.analytics.services.kpis import _tx_qs, detect_transaction_anomalies
from apps.core.permissions import get_user_zone
from apps.operational.models import (
    Mission,
    MissionStatut,
    StatutSync,
    StatutValidation,
    StockCarte,
    Transaction,
)


def run_all_rules(user):
    rules = []
    rules.extend(_rule_transaction_3sigma(user))
    rules.extend(_rule_zero_tx_completed_mission(user))
    rules.extend(_rule_machine_rejection_rate(user))
    rules.extend(_rule_stock_threshold(user))
    rules.extend(_rule_mission_overrun(user))
    rules.extend(_rule_sync_stale(user))
    return rules


def _rule_transaction_3sigma(user):
    anomalies = detect_transaction_anomalies(user)
    return [{
        "rule": "TRANSACTION_3SIGMA",
        "severity": "HIGH",
        "message": f"Transaction {a['numero']} montant anormal (z={a['z_score']})",
        "entity_type": "transaction",
        "entity_id": a["transaction_id"],
        "details": a,
    } for a in anomalies[:20]]


def _rule_zero_tx_completed_mission(user):
    since = timezone.now() - timedelta(days=7)
    qs = Mission.objects.filter(statut=MissionStatut.TERMINEE, date_fin__gte=since)
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(agent__zone_affectation=zone)
    results = []
    for m in qs:
        if m.transactions.count() == 0:
            results.append({
                "rule": "ZERO_TX_COMPLETED_MISSION",
                "severity": "MEDIUM",
                "message": f"Mission terminée sans transaction — agent {m.agent.matricule}",
                "entity_type": "mission",
                "entity_id": str(m.id),
                "details": {"agent": m.agent.matricule, "station": m.station.nom},
            })
    return results


def _rule_machine_rejection_rate(user):
    since = timezone.now() - timedelta(days=30)
    qs = _tx_qs(user, start=since)
    machines = (
        qs.values("machine__id", "machine__numero_serie")
        .annotate(
            total=Count("id"),
            rejected=Count("id", filter=Q(statut_validation=StatutValidation.REJETEE)),
        )
    )
    results = []
    for m in machines:
        if m["total"] >= 10 and m["rejected"] / m["total"] > 0.20:
            results.append({
                "rule": "MACHINE_HIGH_REJECTION",
                "severity": "HIGH",
                "message": f"Machine {m['machine__numero_serie']} taux rejet >20%",
                "entity_type": "machine",
                "entity_id": str(m["machine__id"]),
                "details": {"taux_rejet": round(m["rejected"] / m["total"], 4)},
            })
    return results


def _rule_stock_threshold(user):
    qs = StockCarte.objects.select_related("station")
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(station__missions__agent__zone_affectation=zone).distinct()
    return [{
        "rule": "STOCK_BELOW_THRESHOLD",
        "severity": "MEDIUM",
        "message": f"Stock {s.type_carte} sous seuil à {s.station.nom}",
        "entity_type": "stock",
        "entity_id": str(s.id),
        "details": {"quantite": s.quantite_actuelle, "seuil": s.seuil_alerte},
    } for s in qs if s.quantite_actuelle < s.seuil_alerte]


def _rule_mission_overrun(user):
    since = timezone.now() - timedelta(days=30)
    qs = Mission.objects.filter(statut=MissionStatut.TERMINEE, date_fin__isnull=False, date_debut__gte=since)
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(agent__zone_affectation=zone)
    results = []
    for m in qs:
        actual = (m.date_fin - m.date_debut).total_seconds() / 60
        if actual > m.duree_prevue_minutes * 1.5:
            results.append({
                "rule": "MISSION_OVERRUN",
                "severity": "MEDIUM",
                "message": f"Mission dépasse 150% durée prévue — {m.agent.matricule}",
                "entity_type": "mission",
                "entity_id": str(m.id),
                "details": {
                    "prevue_min": m.duree_prevue_minutes,
                    "reelle_min": round(actual),
                },
            })
    return results


def _rule_sync_stale(user):
    threshold = timezone.now() - timedelta(hours=2)
    qs = Transaction.objects.filter(
        statut_sync__in=[StatutSync.EN_ATTENTE, StatutSync.ECHEC],
        timestamp__lt=threshold,
    )
    zone = get_user_zone(user)
    if zone:
        qs = qs.filter(agent__zone_affectation=zone)
    return [{
        "rule": "SYNC_STALE",
        "severity": "HIGH",
        "message": f"Sync non effectuée >2h — {tx.numero_transaction}",
        "entity_type": "transaction",
        "entity_id": str(tx.id),
        "details": {"timestamp": tx.timestamp.isoformat(), "statut_sync": tx.statut_sync},
    } for tx in qs[:50]]
