import os

from django.http import FileResponse, Http404
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminProfile
from apps.operational.models import Rapport, TypeRapport
from apps.reports.generators import create_rapport, generate_report


class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = (
            "id", "type_rapport", "periode_debut", "periode_fin",
            "statut_generation", "fichier_url", "date_generation",
        )


class RapportGenerateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminProfile]

    def post(self, request):
        type_rapport = request.data.get("type_rapport", TypeRapport.QUOTIDIEN)
        if type_rapport not in TypeRapport.values:
            return Response({"detail": "Type invalide"}, status=status.HTTP_400_BAD_REQUEST)
        rapport = create_rapport(type_rapport, request.user)
        try:
            filepath = generate_report(rapport, request.user)
            return Response(RapportSerializer(rapport).data | {"filepath": filepath})
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RapportExportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminProfile]

    def get(self, request, rapport_id):
        try:
            rapport = Rapport.objects.get(id=rapport_id)
        except Rapport.DoesNotExist:
            raise Http404
        if not rapport.fichier_url or not os.path.exists(rapport.fichier_url):
            return Response({"detail": "Fichier non disponible"}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(open(rapport.fichier_url, "rb"), as_attachment=True,
                            filename=os.path.basename(rapport.fichier_url))


class RapportListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminProfile]

    def get(self, request):
        rapports = Rapport.objects.order_by("-date_generation")[:50]
        return Response(RapportSerializer(rapports, many=True).data)
