from django.db import connection
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Platform health check — verifies DB and cache connectivity."""
    checks = {
        "status": "ok",
        "service": "tpvs-backend",
        "timestamp": timezone.now().isoformat(),
        "checks": {},
    }

    # MySQL (operational)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["checks"]["mysql"] = "ok"
    except Exception as exc:
        checks["checks"]["mysql"] = f"error: {exc}"
        checks["status"] = "degraded"

    # PostgreSQL (DWH)
    try:
        from django.db import connections

        with connections["dwh"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["checks"]["postgres_dwh"] = "ok"
    except Exception as exc:
        checks["checks"]["postgres_dwh"] = f"error: {exc}"
        checks["status"] = "degraded"

    # Redis
    try:
        from django.core.cache import cache

        cache.set("health_check", "ok", timeout=10)
        cache.get("health_check")
        checks["checks"]["redis"] = "ok"
    except Exception as exc:
        checks["checks"]["redis"] = f"error: {exc}"
        checks["status"] = "degraded"

    status_code = 200 if checks["status"] == "ok" else 503
    return Response(checks, status=status_code)
