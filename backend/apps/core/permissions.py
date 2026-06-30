"""Shared RBAC permission classes and zone-scoping utilities."""
from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.SUPER_ADMIN


class IsAdminProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_profile


class IsFinanceOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            UserRole.SUPER_ADMIN, UserRole.ADMIN_FINANCE,
        )


class IsTechniqueOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            UserRole.SUPER_ADMIN, UserRole.ADMIN_TECHNIQUE,
        )


class IsOperationalOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            UserRole.SUPER_ADMIN, UserRole.ADMIN_OPERATIONNEL,
        )


def get_user_zone(user):
    """Return zone filter for Admin Opérationnel; None means all zones."""
    if user.role == UserRole.ADMIN_OPERATIONNEL and user.zone_affectation:
        return user.zone_affectation
    return None


def filter_by_zone(qs, user, zone_field="zone_affectation"):
    zone = get_user_zone(user)
    if zone:
        return qs.filter(**{zone_field: zone})
    if user.role == UserRole.AGENT:
        return qs.filter(id=user.id) if zone_field == "zone_affectation" else qs.filter(agent=user)
    return qs


def anonymize_agent_data(data: dict, user) -> dict:
    """Mask sensitive fields for non-finance profiles."""
    if user.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN_FINANCE):
        return data
    if "matricule" in data:
        data = {**data, "matricule": data["matricule"][:4] + "****"}
    return data
