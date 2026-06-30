import uuid

from django.conf import settings
from django.db import models


class TypeStation(models.TextChoices):
    STATION_TRAM = "STATION_TRAM", "Station Tram"
    STATION_BUS = "STATION_BUS", "Station Bus"
    STATION_METRO = "STATION_METRO", "Station Métro"
    HUB_INTERMODAL = "HUB_INTERMODAL", "Hub Intermodal"


class StationStatut(models.TextChoices):
    OUVERTE = "OUVERTE", "Ouverte"
    FERMEE = "FERMEE", "Fermée"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    SATUREE = "SATUREE", "Saturée"


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=200)
    type_station = models.CharField(max_length=30, choices=TypeStation.choices)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    lignes_desservies = models.JSONField(default=list, blank=True)
    statut = models.CharField(
        max_length=20, choices=StationStatut.choices, default=StationStatut.OUVERTE
    )

    class Meta:
        db_table = "station"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class MachineStatut(models.TextChoices):
    DISPONIBLE = "DISPONIBLE", "Disponible"
    EN_PANNE = "EN_PANNE", "En panne"
    EN_MAINTENANCE = "EN_MAINTENANCE", "En maintenance"
    HORS_SERVICE = "HORS_SERVICE", "Hors service"


class Machine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_serie = models.CharField(max_length=64, unique=True)
    modele = models.CharField(max_length=100)
    type_station = models.CharField(max_length=30, choices=TypeStation.choices)
    statut = models.CharField(
        max_length=20, choices=MachineStatut.choices, default=MachineStatut.DISPONIBLE
    )
    batterie = models.PositiveSmallIntegerField(default=100)
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="machines")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        db_table = "machine"
        ordering = ["numero_serie"]

    def __str__(self):
        return self.numero_serie


class MissionStatut(models.TextChoices):
    PLANIFIEE = "PLANIFIEE", "Planifiée"
    EN_COURS = "EN_COURS", "En cours"
    TERMINEE = "TERMINEE", "Terminée"
    ANNULEE = "ANNULEE", "Annulée"


class Mission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="missions"
    )
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="missions")
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="missions")
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20, choices=MissionStatut.choices, default=MissionStatut.PLANIFIEE
    )
    zone_couverture = models.CharField(max_length=100)
    donnees_telechargees = models.BooleanField(default=False)
    description = models.TextField(blank=True, default="")
    duree_prevue_minutes = models.PositiveIntegerField(default=480)
    cause_annulation = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "mission"
        ordering = ["-date_debut"]

    def __str__(self):
        return f"Mission {self.id} — {self.agent}"


class TypePaiement(models.TextChoices):
    CB = "CB", "Carte bancaire"
    TRANSPORT = "TRANSPORT", "Transport"
    ESPECES = "ESPECES", "Espèces"
    MOBILE = "MOBILE", "Mobile"


class StatutValidation(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    VALIDEE = "VALIDEE", "Validée"
    REJETEE = "REJETEE", "Rejetée"


class StatutSync(models.TextChoices):
    SYNC = "SYNC", "Synchronisé"
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    ECHEC = "ECHEC", "Échec"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(
        Mission, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transactions"
    )
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="transactions")
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="transactions")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_paiement = models.CharField(max_length=20, choices=TypePaiement.choices)
    statut_validation = models.CharField(
        max_length=20, choices=StatutValidation.choices, default=StatutValidation.EN_ATTENTE
    )
    statut_sync = models.CharField(
        max_length=20, choices=StatutSync.choices, default=StatutSync.EN_ATTENTE
    )
    timestamp = models.DateTimeField(db_index=True)
    numero_transaction = models.CharField(max_length=64, unique=True)
    type_carte = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "transaction"
        ordering = ["-timestamp"]

    def __str__(self):
        return self.numero_transaction


class TypeCarte(models.TextChoices):
    NAVIGO = "NAVIGO", "Navigo"
    TICKET_T_PLUS = "TICKET_T_PLUS", "Ticket t+"
    CARTE_JEUNE = "CARTE_JEUNE", "Carte Jeune"
    CARTE_SENIOR = "CARTE_SENIOR", "Carte Senior"
    PASS_JOUR = "PASS_JOUR", "Pass Jour"


class StockCarte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_carte = models.CharField(max_length=30, choices=TypeCarte.choices)
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="stocks")
    quantite_actuelle = models.PositiveIntegerField()
    quantite_initiale = models.PositiveIntegerField()
    seuil_alerte = models.PositiveIntegerField(default=50)
    taux_defectueux = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stock_carte"
        unique_together = [("type_carte", "station")]
        ordering = ["station", "type_carte"]

    def __str__(self):
        return f"{self.type_carte} @ {self.station}"


class TypeRapport(models.TextChoices):
    QUOTIDIEN = "QUOTIDIEN", "Quotidien"
    HEBDOMADAIRE = "HEBDOMADAIRE", "Hebdomadaire"
    MENSUEL = "MENSUEL", "Mensuel"
    PERFORMANCE = "PERFORMANCE", "Performance"
    STOCK = "STOCK", "Stock"
    TRANSACTION = "TRANSACTION", "Transaction"
    DEFECTUEUX = "DEFECTUEUX", "Défectueux"
    STATION = "STATION", "Station"


class StatutGeneration(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    EN_COURS = "EN_COURS", "En cours"
    TERMINE = "TERMINE", "Terminé"
    ECHEC = "ECHEC", "Échec"


class Rapport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_rapport = models.CharField(max_length=20, choices=TypeRapport.choices)
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    donnees = models.JSONField(default=dict, blank=True)
    statut_generation = models.CharField(
        max_length=20, choices=StatutGeneration.choices, default=StatutGeneration.EN_ATTENTE
    )
    fichier_url = models.CharField(max_length=500, blank=True, default="")
    date_generation = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "rapport"
        ordering = ["-date_generation"]

    def __str__(self):
        return f"{self.type_rapport} ({self.periode_debut} — {self.periode_fin})"


class TypeMoto(models.TextChoices):
    ELECTRIQUE = "ELECTRIQUE", "Électrique"
    THERMIQUE = "THERMIQUE", "Thermique"


class StatutMoto(models.TextChoices):
    DISPONIBLE = "DISPONIBLE", "Disponible"
    EN_MISSION = "EN_MISSION", "En mission"
    EN_MAINTENANCE = "EN_MAINTENANCE", "En maintenance"
    HORS_SERVICE = "HORS_SERVICE", "Hors service"


class Moto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_moto = models.CharField(max_length=20, choices=TypeMoto.choices)
    autonomie = models.PositiveIntegerField(help_text="Autonomie en km")
    niveau_batterie = models.PositiveSmallIntegerField(default=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    position_timestamp = models.DateTimeField()
    statut_moto = models.CharField(
        max_length=20, choices=StatutMoto.choices, default=StatutMoto.DISPONIBLE
    )
    kilometrage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    agent_assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="motos",
    )

    class Meta:
        db_table = "moto"
        ordering = ["id"]

    def __str__(self):
        return f"Moto {self.id} ({self.type_moto})"


class MotoPositionHistory(models.Model):
    """GPS ping history for motos — used by ETL and trajectory replay."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    moto = models.ForeignKey(Moto, on_delete=models.CASCADE, related_name="positions")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(db_index=True)
    kilometrage = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "moto_position_history"
        ordering = ["-timestamp"]


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=200, blank=True, default="")
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-timestamp"]
