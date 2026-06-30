from django.urls import path

from . import views

urlpatterns = [
    path("", views.AnomalyListView.as_view(), name="anomalies-list"),
]
