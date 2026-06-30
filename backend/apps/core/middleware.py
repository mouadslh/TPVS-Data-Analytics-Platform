from django.utils.deprecation import MiddlewareMixin

from apps.operational.models import AuditLog


class AuditLogMiddleware(MiddlewareMixin):
    """Log authenticated API mutations."""

    LOGGED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def process_response(self, request, response):
        if (
            request.method in self.LOGGED_METHODS
            and request.path.startswith("/api/")
            and hasattr(request, "user")
            and request.user.is_authenticated
            and response.status_code < 400
        ):
            AuditLog.objects.create(
                user=request.user,
                action=f"{request.method} {request.path}",
                resource=request.path,
                details={"query": dict(request.GET)},
                ip_address=self._get_ip(request),
            )
        return response

    def _get_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
