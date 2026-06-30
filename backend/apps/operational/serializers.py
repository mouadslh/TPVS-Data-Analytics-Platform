from rest_framework import serializers

from apps.operational.models import Mission, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    agent_nom = serializers.CharField(source="agent.matricule", read_only=True)
    station_nom = serializers.CharField(source="station.nom", read_only=True)
    machine_serie = serializers.CharField(source="machine.numero_serie", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id", "numero_transaction", "montant", "type_paiement",
            "statut_validation", "statut_sync", "timestamp", "type_carte",
            "agent_nom", "station_nom", "machine_serie",
        )


class MissionSerializer(serializers.ModelSerializer):
    agent_nom = serializers.CharField(source="agent.matricule", read_only=True)
    station_nom = serializers.CharField(source="station.nom", read_only=True)

    class Meta:
        model = Mission
        fields = (
            "id", "agent_nom", "station_nom", "date_debut", "date_fin",
            "statut", "zone_couverture", "duree_prevue_minutes", "description",
        )
