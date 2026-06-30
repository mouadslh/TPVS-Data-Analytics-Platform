"""Synthetic data generator for development and testing."""
import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import UserRole, UserStatut
from apps.operational.models import (
    Machine,
    MachineStatut,
    Mission,
    MissionStatut,
    Moto,
    MotoPositionHistory,
    Station,
    StationStatut,
    StatutMoto,
    StatutSync,
    StatutValidation,
    StockCarte,
    Transaction,
    TypeCarte,
    TypeMoto,
    TypePaiement,
    TypeStation,
)

User = get_user_model()

ZONES = ["Paris Nord", "Paris Sud", "Paris Est", "Paris Ouest", "Banlieue Nord", "Banlieue Sud"]
LIGNES = ["T1", "T2", "T3", "M1", "M4", "M7", "M14", "Bus 21", "Bus 38", "Bus 62"]
PARIS_COORDS = [
    (48.8566, 2.3522), (48.8738, 2.2950), (48.8440, 2.3750),
    (48.8606, 2.3376), (48.8530, 2.3499), (48.8675, 2.3631),
    (48.8380, 2.3200), (48.8820, 2.3400), (48.8500, 2.3900),
    (48.8700, 2.3100), (48.8300, 2.3600), (48.8900, 2.2800),
]


class Command(BaseCommand):
    help = "Seed operational database with synthetic TPVS data"

    def add_arguments(self, parser):
        parser.add_argument("--agents", type=int, default=50)
        parser.add_argument("--days", type=int, default=180)
        parser.add_argument("--flush", action="store_true", help="Clear existing seed data first")

    def handle(self, *args, **options):
        agents_count = options["agents"]
        days = options["days"]

        if options["flush"]:
            self._flush()

        self.stdout.write("Creating admin users...")
        self._create_admins()

        self.stdout.write(f"Creating {agents_count} agents...")
        agents = self._create_agents(agents_count)

        self.stdout.write("Creating stations and machines...")
        stations = self._create_stations()
        machines = self._create_machines(stations)

        self.stdout.write("Creating motos...")
        motos = self._create_motos(agents)

        self.stdout.write("Creating stock...")
        self._create_stock(stations)

        self.stdout.write(f"Generating {days} days of missions and transactions...")
        self._create_missions_and_transactions(agents, stations, machines, days)

        self.stdout.write("Generating moto GPS history...")
        self._create_moto_positions(motos, days)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {agents_count} agents, {len(stations)} stations, "
            f"{Transaction.objects.count()} transactions over {days} days."
        ))

    def _flush(self):
        Transaction.objects.all().delete()
        Mission.objects.all().delete()
        MotoPositionHistory.objects.all().delete()
        Moto.objects.all().delete()
        StockCarte.objects.all().delete()
        Machine.objects.all().delete()
        Station.objects.all().delete()
        User.objects.filter(role=UserRole.AGENT).delete()

    def _create_admins(self):
        admins = [
            ("admin", UserRole.SUPER_ADMIN, "", "Admin", "Super"),
            ("op.nord", UserRole.ADMIN_OPERATIONNEL, "Paris Nord", "Dupont", "Marie"),
            ("finance", UserRole.ADMIN_FINANCE, "", "Martin", "Jean"),
            ("tech", UserRole.ADMIN_TECHNIQUE, "", "Bernard", "Luc"),
        ]
        for username, role, zone, nom, prenom in admins:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password="changeme123",
                    email=f"{username}@tpvs.local",
                    matricule=f"ADM-{username.upper()[:6]}",
                    nom=nom,
                    prenom=prenom,
                    zone_affectation=zone,
                    role=role,
                    statut=UserStatut.ACTIF,
                    is_staff=True,
                    is_superuser=(role == UserRole.SUPER_ADMIN),
                )

    def _create_agents(self, count):
        agents = []
        for i in range(count):
            zone = random.choice(ZONES)
            matricule = f"AGT-{i+1:04d}"
            if User.objects.filter(matricule=matricule).exists():
                continue
            agent = User.objects.create_user(
                username=f"agent{i+1}",
                password="changeme123",
                email=f"agent{i+1}@tpvs.local",
                matricule=matricule,
                nom=random.choice(["Durand", "Petit", "Moreau", "Leroy", "Roux", "Fournier"]),
                prenom=random.choice(["Alice", "Bob", "Claire", "David", "Emma", "François"]),
                zone_affectation=zone,
                niveau_accreditation=random.randint(1, 5),
                mode_hors_ligne=random.random() < 0.15,
                role=UserRole.AGENT,
                statut=random.choices(
                    [UserStatut.ACTIF, UserStatut.INACTIF, UserStatut.SUSPENDU],
                    weights=[0.85, 0.10, 0.05],
                )[0],
            )
            agents.append(agent)
        return list(User.objects.filter(role=UserRole.AGENT))

    def _create_stations(self):
        stations = []
        types = list(TypeStation.choices)
        for i, (lat, lng) in enumerate(PARIS_COORDS):
            nom = f"Station {['République', 'Nation', 'Bastille', 'Opéra', 'Gare du Nord', 'Montparnasse', 'Châtelet', 'Belleville', 'La Défense', 'Vincennes', 'Issy', 'Saint-Denis'][i]}"
            station = Station.objects.create(
                nom=nom,
                type_station=random.choice(types)[0],
                latitude=Decimal(str(lat + random.uniform(-0.01, 0.01))),
                longitude=Decimal(str(lng + random.uniform(-0.01, 0.01))),
                lignes_desservies=random.sample(LIGNES, k=random.randint(2, 5)),
                statut=random.choices(
                    [StationStatut.OUVERTE, StationStatut.MAINTENANCE, StationStatut.SATUREE],
                    weights=[0.85, 0.10, 0.05],
                )[0],
            )
            stations.append(station)
        return stations

    def _create_machines(self, stations):
        machines = []
        for i in range(len(stations) * 3):
            station = stations[i % len(stations)]
            machines.append(Machine.objects.create(
                numero_serie=f"TPVS-{i+1:05d}",
                modele=random.choice(["TPVS-100", "TPVS-200", "TPVS-Pro"]),
                type_station=station.type_station,
                statut=random.choices(
                    list(MachineStatut.values),
                    weights=[0.75, 0.10, 0.10, 0.05],
                )[0],
                batterie=random.randint(10, 100),
                station=station,
                latitude=station.latitude,
                longitude=station.longitude,
            ))
        return machines

    def _create_motos(self, agents):
        motos = []
        active_agents = [a for a in agents if a.statut == UserStatut.ACTIF]
        for i in range(min(20, len(active_agents))):
            lat, lng = random.choice(PARIS_COORDS)
            motos.append(Moto.objects.create(
                type_moto=random.choice(list(TypeMoto.values)),
                autonomie=random.randint(40, 120),
                niveau_batterie=random.randint(20, 100),
                latitude=Decimal(str(lat)),
                longitude=Decimal(str(lng)),
                position_timestamp=timezone.now(),
                statut_moto=random.choice(list(StatutMoto.values)),
                kilometrage=Decimal(str(random.randint(500, 15000))),
                agent_assigne=active_agents[i] if i < len(active_agents) else None,
            ))
        return motos

    def _create_stock(self, stations):
        for station in stations:
            for carte_type in TypeCarte.values:
                StockCarte.objects.create(
                    type_carte=carte_type,
                    station=station,
                    quantite_actuelle=random.randint(20, 500),
                    quantite_initiale=500,
                    seuil_alerte=random.randint(30, 80),
                    taux_defectueux=Decimal(str(round(random.uniform(0, 0.08), 4))),
                )

    def _create_missions_and_transactions(self, agents, stations, machines, days):
        now = timezone.now()
        start = now - timedelta(days=days)
        tx_count = 0

        for day_offset in range(days):
            day = start + timedelta(days=day_offset)
            daily_missions = random.randint(15, 40)

            for _ in range(daily_missions):
                agent = random.choice(agents)
                station = random.choice(stations)
                station_machines = [m for m in machines if m.station_id == station.id]
                machine = random.choice(station_machines) if station_machines else random.choice(machines)

                mission_start = day.replace(
                    hour=random.randint(6, 18),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0,
                )
                duree_prevue = random.randint(240, 600)
                statut = random.choices(
                    [MissionStatut.TERMINEE, MissionStatut.EN_COURS, MissionStatut.ANNULEE, MissionStatut.PLANIFIEE],
                    weights=[0.70, 0.10, 0.08, 0.12],
                )[0]

                if day_offset >= days - 1 and statut == MissionStatut.TERMINEE:
                    statut = MissionStatut.EN_COURS

                date_fin = None
                if statut == MissionStatut.TERMINEE:
                    overrun = random.random() < 0.12
                    actual = int(duree_prevue * (1.6 if overrun else random.uniform(0.8, 1.1)))
                    date_fin = mission_start + timedelta(minutes=actual)
                elif statut == MissionStatut.ANNULEE:
                    date_fin = mission_start + timedelta(minutes=random.randint(30, 120))

                mission = Mission.objects.create(
                    agent=agent,
                    station=station,
                    machine=machine,
                    date_debut=mission_start,
                    date_fin=date_fin,
                    statut=statut,
                    zone_couverture=agent.zone_affectation,
                    donnees_telechargees=random.random() < 0.9,
                    description=f"Mission terrain {station.nom}",
                    duree_prevue_minutes=duree_prevue,
                    cause_annulation=random.choice(["Météo", "Panne machine", "Agent indisponible", ""]) if statut == MissionStatut.ANNULEE else "",
                )

                if statut in (MissionStatut.TERMINEE, MissionStatut.EN_COURS):
                    nb_tx = 0 if (statut == MissionStatut.TERMINEE and random.random() < 0.03) else random.randint(5, 40)
                    for t in range(nb_tx):
                        tx_time = mission_start + timedelta(minutes=random.randint(10, duree_prevue))
                        if date_fin and tx_time > date_fin:
                            tx_time = date_fin - timedelta(minutes=1)

                        validation = random.choices(
                            [StatutValidation.VALIDEE, StatutValidation.REJETEE, StatutValidation.EN_ATTENTE],
                            weights=[0.88, 0.07, 0.05],
                        )[0]

                        Transaction.objects.create(
                            mission=mission,
                            agent=agent,
                            station=station,
                            machine=machine,
                            montant=Decimal(str(round(random.uniform(1.5, 85.0), 2))),
                            type_paiement=random.choice(list(TypePaiement.values)),
                            statut_validation=validation,
                            statut_sync=random.choices(
                                [StatutSync.SYNC, StatutSync.EN_ATTENTE, StatutSync.ECHEC],
                                weights=[0.92, 0.05, 0.03],
                            )[0],
                            timestamp=tx_time,
                            numero_transaction=f"TX-{uuid.uuid4().hex[:12].upper()}",
                            type_carte=random.choice(list(TypeCarte.values)),
                        )
                        tx_count += 1

        self.stdout.write(f"  Created {tx_count} transactions")

    def _create_moto_positions(self, motos, days):
        now = timezone.now()
        for moto in motos:
            lat = float(moto.latitude)
            lng = float(moto.longitude)
            km = float(moto.kilometrage)
            for h in range(0, days * 24, 4):
                ts = now - timedelta(hours=days * 24 - h)
                lat += random.uniform(-0.005, 0.005)
                lng += random.uniform(-0.005, 0.005)
                km += random.uniform(0.5, 3.0)
                MotoPositionHistory.objects.create(
                    moto=moto,
                    latitude=Decimal(str(round(lat, 6))),
                    longitude=Decimal(str(round(lng, 6))),
                    timestamp=ts,
                    kilometrage=Decimal(str(round(km, 2))),
                )
            moto.latitude = Decimal(str(round(lat, 6)))
            moto.longitude = Decimal(str(round(lng, 6)))
            moto.kilometrage = Decimal(str(round(km, 2)))
            moto.position_timestamp = now
            moto.save()
