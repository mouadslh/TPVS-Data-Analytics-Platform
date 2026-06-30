from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.anomalies.engine import run_all_rules
from apps.core.permissions import IsAdminProfile


class AnomalyListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminProfile]

    def get(self, request):
        anomalies = run_all_rules(request.user)
        return Response({"anomalies": anomalies, "count": len(anomalies)})
