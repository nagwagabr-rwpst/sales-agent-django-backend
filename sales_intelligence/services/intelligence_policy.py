from sales_intelligence.models import TenantIntelligencePolicy
from sales_intelligence.services.strategy_profiles import STRATEGY_BALANCED


def get_tenant_intelligence_strategy(tenant):
    strategy = (
        TenantIntelligencePolicy.objects.filter(tenant=tenant, is_active=True)
        .values_list("strategy", flat=True)
        .first()
    )
    return strategy or STRATEGY_BALANCED

