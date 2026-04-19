from django.db import models
from core.models import Tenant


class TenantIntelligencePolicy(models.Model):
    STRATEGY_BALANCED = "balanced"
    STRATEGY_HIGH_VALUE_FOCUS = "high_value_focus"
    STRATEGY_REACTIVATION_FOCUS = "reactivation_focus"

    STRATEGY_CHOICES = [
        (STRATEGY_BALANCED, "Balanced"),
        (STRATEGY_HIGH_VALUE_FOCUS, "High Value Focus"),
        (STRATEGY_REACTIVATION_FOCUS, "Reactivation Focus"),
    ]

    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name="intelligence_policy",
    )
    strategy = models.CharField(
        max_length=32,
        choices=STRATEGY_CHOICES,
        default=STRATEGY_BALANCED,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.code} - {self.strategy}"
