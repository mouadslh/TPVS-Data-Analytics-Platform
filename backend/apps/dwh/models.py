"""Unmanaged Django models mapping to PostgreSQL DWH star schema."""
from django.db import models


class DimDate(models.Model):
    date_id = models.AutoField(primary_key=True)
    date = models.DateField(unique=True)
    jour = models.SmallIntegerField()
    semaine = models.SmallIntegerField()
    mois = models.SmallIntegerField()
    trimestre = models.SmallIntegerField()
    annee = models.SmallIntegerField()
    jour_semaine = models.SmallIntegerField()
    est_ferie = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'dwh"."dim_date'


class DimAgent(models.Model):
    agent_id = models.UUIDField(primary_key=True)
    matricule = models.CharField(max_length=32)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    zone_affectation = models.CharField(max_length=100, blank=True)
    niveau_accreditation = models.SmallIntegerField(null=True)
    statut = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = 'dwh"."dim_agent'


class DimStation(models.Model):
    station_id = models.UUIDField(primary_key=True)
    nom = models.CharField(max_length=200)
    type_station = models.CharField(max_length=30, blank=True)
    localisation = models.CharField(max_length=200, blank=True)
    coords_gps = models.CharField(max_length=50, blank=True)
    statut = models.CharField(max_length=20, blank=True)
    lignes_desservies = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'dwh"."dim_station'


class DimMachine(models.Model):
    machine_id = models.UUIDField(primary_key=True)
    numero_serie = models.CharField(max_length=64)
    modele = models.CharField(max_length=100, blank=True)
    type_machine = models.CharField(max_length=30, blank=True)
    localisation = models.CharField(max_length=200, blank=True)
    statut = models.CharField(max_length=20, blank=True)
    batterie = models.SmallIntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'dwh"."dim_machine'


class DimMission(models.Model):
    mission_id = models.UUIDField(primary_key=True)
    zone_couverture = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'dwh"."dim_mission'


class DimCarte(models.Model):
    carte_type_id = models.AutoField(primary_key=True)
    type_carte = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        managed = False
        db_table = 'dwh"."dim_carte'


class FactTransaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    date_id = models.IntegerField(null=True)
    agent_id = models.UUIDField(null=True)
    station_id = models.UUIDField(null=True)
    machine_id = models.UUIDField(null=True)
    mission_id = models.UUIDField(null=True)
    carte_type_id = models.IntegerField(null=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_paiement = models.CharField(max_length=20, blank=True)
    statut_validation = models.CharField(max_length=20, blank=True)
    statut_sync = models.CharField(max_length=20, blank=True)
    numero_transaction = models.CharField(max_length=64)
    loaded_at = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'dwh"."fact_transactions'


class FactPerformance(models.Model):
    id = models.AutoField(primary_key=True)
    date_id = models.IntegerField(null=True)
    agent_id = models.UUIDField(null=True)
    nb_transactions = models.IntegerField(default=0)
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taux_validation = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    score_performance = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    nb_missions = models.IntegerField(default=0)
    taux_completion = models.DecimalField(max_digits=5, decimal_places=4, default=0)

    class Meta:
        managed = False
        db_table = 'dwh"."fact_performances'
