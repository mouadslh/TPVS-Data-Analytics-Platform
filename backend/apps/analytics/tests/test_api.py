import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.operational.models import Station, TypeStation

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="testadmin",
        password="testpass123",
        matricule="ADM-TEST",
        nom="Test",
        prenom="Admin",
        role="SUPER_ADMIN",
        is_staff=True,
    )


@pytest.fixture
def station(db):
    return Station.objects.create(
        nom="Test Station",
        type_station=TypeStation.STATION_METRO,
        latitude=48.8566,
        longitude=2.3522,
        lignes_desservies=["M1"],
    )


@pytest.mark.django_db
def test_login_success(api_client, admin_user):
    response = api_client.post("/api/auth/login/", {"username": "testadmin", "password": "testpass123"})
    assert response.status_code == 200
    assert "access" in response.json()


@pytest.mark.django_db
def test_login_failure(api_client, admin_user):
    response = api_client.post("/api/auth/login/", {"username": "testadmin", "password": "wrong"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_executive_dashboard_requires_auth(api_client):
    response = api_client.get("/api/analytics/dashboard/executive/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_executive_dashboard(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/analytics/dashboard/executive/")
    assert response.status_code == 200
    assert "banner" in response.json()


@pytest.mark.django_db
def test_anomalies_endpoint(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/anomalies/")
    assert response.status_code == 200
    assert "anomalies" in response.json()
