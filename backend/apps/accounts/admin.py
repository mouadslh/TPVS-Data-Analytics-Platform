from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "matricule", "nom", "prenom", "role", "zone_affectation", "statut", "is_active",
    )
    list_filter = ("role", "statut", "zone_affectation")
    search_fields = ("matricule", "nom", "prenom", "username", "email")
    ordering = ("matricule",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("TPVS", {
            "fields": (
                "matricule", "nom", "prenom", "zone_affectation",
                "niveau_accreditation", "mode_hors_ligne", "statut", "role",
            ),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("TPVS", {
            "fields": (
                "matricule", "nom", "prenom", "zone_affectation",
                "niveau_accreditation", "mode_hors_ligne", "statut", "role",
            ),
        }),
    )
