from django.contrib import admin

from .models import (
    Machine,
    Mission,
    Moto,
    MotoPositionHistory,
    Rapport,
    Station,
    StockCarte,
    Transaction,
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("nom", "type_station", "statut", "latitude", "longitude")
    list_filter = ("type_station", "statut")
    search_fields = ("nom",)


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("numero_serie", "modele", "station", "statut", "batterie")
    list_filter = ("statut", "type_station")
    search_fields = ("numero_serie", "modele")


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("id", "agent", "station", "statut", "date_debut", "date_fin")
    list_filter = ("statut", "zone_couverture")
    date_hierarchy = "date_debut"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "numero_transaction", "agent", "station", "montant",
        "type_paiement", "statut_validation", "timestamp",
    )
    list_filter = ("statut_validation", "type_paiement", "statut_sync")
    date_hierarchy = "timestamp"
    search_fields = ("numero_transaction",)


@admin.register(StockCarte)
class StockCarteAdmin(admin.ModelAdmin):
    list_display = (
        "type_carte", "station", "quantite_actuelle", "seuil_alerte", "taux_defectueux",
    )
    list_filter = ("type_carte",)


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ("type_rapport", "periode_debut", "periode_fin", "statut_generation")
    list_filter = ("type_rapport", "statut_generation")


@admin.register(Moto)
class MotoAdmin(admin.ModelAdmin):
    list_display = ("id", "type_moto", "statut_moto", "kilometrage", "agent_assigne")
    list_filter = ("type_moto", "statut_moto")


@admin.register(MotoPositionHistory)
class MotoPositionHistoryAdmin(admin.ModelAdmin):
    list_display = ("moto", "timestamp", "latitude", "longitude")
    date_hierarchy = "timestamp"
