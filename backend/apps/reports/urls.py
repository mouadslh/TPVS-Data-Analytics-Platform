from django.urls import path

from . import views

urlpatterns = [
    path("", views.RapportListView.as_view(), name="rapports-list"),
    path("generate/", views.RapportGenerateView.as_view(), name="rapports-generate"),
    path("export/<uuid:rapport_id>/", views.RapportExportView.as_view(), name="rapports-export"),
]
