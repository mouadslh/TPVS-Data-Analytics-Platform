import pytest
from django.contrib.auth import get_user_model

from apps.analytics.services.kpis import kpi_executive_banner, kpi_transactions_summary

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="kpiadmin", password="x", matricule="KPI", nom="K", prenom="P", role="SUPER_ADMIN",
    )


@pytest.mark.django_db
def test_executive_banner_returns_keys(admin_user):
    result = kpi_executive_banner(admin_user)
    assert "ca_jour" in result
    assert "agents_actifs" in result


@pytest.mark.django_db
def test_transactions_summary_empty(admin_user):
    result = kpi_transactions_summary(admin_user)
    assert result["volume"] == 0
    assert result["ca_total"] == 0
