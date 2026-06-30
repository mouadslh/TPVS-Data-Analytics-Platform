from datetime import timedelta

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.services import kpis
from apps.core.permissions import IsAdminProfile
from apps.operational.models import Mission, Transaction
from apps.operational.serializers import MissionSerializer, TransactionSerializer


class ExecutiveDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminProfile]

    def get(self, request):
        return Response({
            "banner": kpis.kpi_executive_banner(request.user),
            "ca_evolution": kpis.kpi_ca_evolution(request.user),
            "top_agents": kpis.kpi_top_agents(request.user),
            "top_stations": kpis.kpi_top_stations(request.user),
        })


class TransactionsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        start = timezone.now() - timedelta(days=days)
        return Response({
            "summary": kpis.kpi_transactions_summary(request.user, start),
            "heatmap": kpis.kpi_hourly_heatmap(request.user, days),
            "n_vs_n1": kpis.kpi_n_vs_n1(request.user),
            "anomalies": kpis.detect_transaction_anomalies(request.user),
            "monthly": kpis.kpi_monthly_evolution(request.user),
        })


class TransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        from apps.core.permissions import get_user_zone

        days = int(self.request.query_params.get("days", 30))
        start = timezone.now() - timedelta(days=days)
        qs = Transaction.objects.select_related("agent", "station", "machine").filter(timestamp__gte=start)
        zone = get_user_zone(self.request.user)
        if zone:
            qs = qs.filter(agent__zone_affectation=zone)
        statut = self.request.query_params.get("statut_validation")
        if statut:
            qs = qs.filter(statut_validation=statut)
        return qs.order_by("-timestamp")[:1000]


class AgentPerformanceView(APIView):
    permission_classes = [IsAuthenticated, IsAdminProfile]

    def get(self, request):
        months = int(request.query_params.get("months", 3))
        return Response(kpis.kpi_agent_performance(request.user, months))


class MissionsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(kpis.kpi_missions_summary(request.user))


class MissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MissionSerializer

    def get_queryset(self):
        qs = Mission.objects.select_related("agent", "station", "machine")
        from apps.core.permissions import get_user_zone
        zone = get_user_zone(self.request.user)
        if zone:
            qs = qs.filter(agent__zone_affectation=zone)
        return qs.order_by("-date_debut")[:500]


class StockSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(kpis.kpi_stock_summary(request.user))


class MachinesSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(kpis.kpi_machines_summary(request.user))


class MotosSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(kpis.kpi_motos_summary(request.user))
