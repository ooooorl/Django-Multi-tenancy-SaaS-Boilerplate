from django.conf import settings
from django.http import HttpResponseNotFound

from tenant.models import Tenant


class TenantMiddleware:
    """
    Middleware to identify and attach the current tenant to each request
    based on the subdomain (e.g., acme.example.com → acme tenant).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self._get_tenant_from_request(request)

        # If _get_tenant_from_request() returned an HttpResponse, return it directly
        if isinstance(tenant, HttpResponseNotFound):
            return tenant

        request.tenant = tenant
        return self.get_response(request)

    def _get_tenant_from_request(self, request):
        """Extracts and returns the tenant based on the subdomain."""
        host = request.get_host().split(":")[0]  # Strip port if exists
        main_domain = getattr(settings, "MAIN_DOMAIN", None)

        if not main_domain:
            raise RuntimeError("MAIN_DOMAIN must be set in settings or .env")

        subdomain = None

        # Extract subdomain if it exists (e.g., acme from acme.example.com)
        if host.endswith(main_domain) and host != main_domain:
            subdomain_part = host.replace(f".{main_domain}", "")
            subdomain = subdomain_part.lower() if subdomain_part else None

        # No subdomain → main site
        if not subdomain:
            return None

        # Try to fetch tenant
        try:
            return Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            return HttpResponseNotFound("Tenant not found.")
