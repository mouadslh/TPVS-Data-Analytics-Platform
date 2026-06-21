import pytest
from django.urls import reverse


@pytest.mark.django_db(databases=["default", "dwh"])
def test_health_check_returns_ok(client):
    response = client.get(reverse("health-check"))
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "tpvs-backend"
    assert "checks" in data
