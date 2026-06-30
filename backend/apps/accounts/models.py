import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
    ADMIN_OPERATIONNEL = "ADMIN_OPERATIONNEL", "Admin Opérationnel"
    ADMIN_FINANCE = "ADMIN_FINANCE", "Admin Finance"
    ADMIN_TECHNIQUE = "ADMIN_TECHNIQUE", "Admin Technique"
    AGENT = "AGENT", "Agent"


class UserStatut(models.TextChoices):
    ACTIF = "ACTIF", "Actif"
    INACTIF = "INACTIF", "Inactif"
    SUSPENDU = "SUSPENDU", "Suspendu"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(max_length=32, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    zone_affectation = models.CharField(max_length=100, blank=True, default="")
    niveau_accreditation = models.PositiveSmallIntegerField(default=1)
    mode_hors_ligne = models.BooleanField(default=False)
    statut = models.CharField(
        max_length=20, choices=UserStatut.choices, default=UserStatut.ACTIF
    )
    role = models.CharField(max_length=30, choices=UserRole.choices, default=UserRole.AGENT)

    class Meta:
        db_table = "utilisateur"
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.matricule} — {self.prenom} {self.nom}"

    @property
    def is_admin_profile(self):
        return self.role != UserRole.AGENT
