from .models import SalesAgent


from dataclasses import dataclass

from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import NotAuthenticated, PermissionDenied


@dataclass(frozen=True)
class SalesAgentContext:
    sales_agent: SalesAgent
    tenant: "Tenant"


def resolve_sales_agent_context(user) -> SalesAgentContext:
    """
    Phase 1 strict rule:
    - Never trust tenant_id / agent_id from client
    - Derive SalesAgent + Tenant from the authenticated user only
    """
    if user is None or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        raise NotAuthenticated()

    try:
        sales_agent = SalesAgent.objects.select_related("tenant").get(user=user)
    except SalesAgent.DoesNotExist:
        raise PermissionDenied("User is not a sales agent.")

    if not sales_agent.is_active:
        raise PermissionDenied("Sales agent is inactive.")

    tenant = sales_agent.tenant
    if not tenant.is_active:
        raise PermissionDenied("Tenant is inactive.")

    return SalesAgentContext(sales_agent=sales_agent, tenant=tenant)