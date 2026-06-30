from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/executive/", views.ExecutiveDashboardView.as_view(), name="executive-dashboard"),
    path("transactions/summary/", views.TransactionsSummaryView.as_view(), name="transactions-summary"),
    path("transactions/", views.TransactionListView.as_view(), name="transactions-list"),
    path("agents/performance/", views.AgentPerformanceView.as_view(), name="agent-performance"),
    path("missions/summary/", views.MissionsSummaryView.as_view(), name="missions-summary"),
    path("missions/", views.MissionListView.as_view(), name="missions-list"),
    path("stock/", views.StockSummaryView.as_view(), name="stock-summary"),
    path("machines/", views.MachinesSummaryView.as_view(), name="machines-summary"),
    path("motos/", views.MotosSummaryView.as_view(), name="motos-summary"),
]
