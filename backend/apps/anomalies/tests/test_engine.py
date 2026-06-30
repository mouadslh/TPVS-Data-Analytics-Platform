import pytest
from django.contrib.auth import get_user_model

from apps.anomalies.engine import run_all_rules
from apps.operational.models import Station, TypeStation

User = get_user_model()


@pytest.mark.django_db
def test_stock_threshold_rule(admin_user, station):
    from apps.operational.models import StockCarte, TypeCarte
    StockCarte.objects.create(
        type_carte=TypeCarte.NAVIGO,
        station=station,
        quantite_actuelle=10,
        quantite_initiale=500,
        seuil_alerte=50,
    )
    admin = User.objects.create_user(
        username="super", password="x", matricule="SA", nom="S", prenom="A", role="SUPER_ADMIN",
    )
    results = run_all_rules(admin)
    stock_rules = [r for r in results if r["rule"] == "STOCK_BELOW_THRESHOLD"]
    assert len(stock_rules) >= 1


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="super", password="x", matricule="SA", nom="S", prenom="A", role="SUPER_ADMIN",
    )


@pytest.fixture
def station(db):
    return Station.objects.create(
        nom="S1", type_station=TypeStation.STATION_BUS,
        latitude=48.85, longitude=2.35, lignes_desservies=["Bus21"],
    )
