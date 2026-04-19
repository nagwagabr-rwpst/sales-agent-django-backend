from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from accounts.models import SalesAgent
from core.models import Tenant
from odoo.models import OfflineSalesOrder
from sales_intelligence.models import TenantIntelligencePolicy
from sales_intelligence.services.prioritization import get_prioritized_customers


class TenantIntelligenceStrategyTests(TestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name="Tenant A", code="tenant-a")
        self.tenant_b = Tenant.objects.create(name="Tenant B", code="tenant-b")

        self.user_a = User.objects.create_user(username="agent-a", password="pass12345")
        self.user_b = User.objects.create_user(username="agent-b", password="pass12345")

        self.agent_a = SalesAgent.objects.create(user=self.user_a, tenant=self.tenant_a)
        self.agent_b = SalesAgent.objects.create(user=self.user_b, tenant=self.tenant_b)

    def _create_order(self, tenant, agent, customer_id, days_ago, status):
        created_at = timezone.now() - timedelta(days=days_ago)
        order = OfflineSalesOrder.objects.create(
            tenant=tenant,
            sales_agent=agent,
            customer_id=customer_id,
            payload={"customer_id": customer_id, "items": []},
            status=status,
        )
        OfflineSalesOrder.objects.filter(pk=order.pk).update(created_at=created_at)
        order.refresh_from_db()
        return order

    def _seed_common_customer_signals(self, tenant, agent, customer_id=101):
        self._create_order(
            tenant=tenant,
            agent=agent,
            customer_id=customer_id,
            days_ago=50,
            status=OfflineSalesOrder.STATUS_SYNCED,
        )
        self._create_order(
            tenant=tenant,
            agent=agent,
            customer_id=customer_id,
            days_ago=50,
            status=OfflineSalesOrder.STATUS_PENDING,
        )
        self._create_order(
            tenant=tenant,
            agent=agent,
            customer_id=customer_id,
            days_ago=50,
            status=OfflineSalesOrder.STATUS_PENDING,
        )

    def _single_result_for_customer(self, tenant, agent, customer_id=101):
        results = get_prioritized_customers(tenant, agent)
        return next(item for item in results if item["customer_id"] == customer_id)

    def test_default_fallback_to_balanced_without_policy(self):
        self._seed_common_customer_signals(self.tenant_a, self.agent_a)

        result = self._single_result_for_customer(self.tenant_a, self.agent_a)

        self.assertEqual(result["suggested_action"], "follow_up")
        self.assertIn(result["priority_level"], {"low", "medium", "high"})

    def test_balanced_strategy_policy(self):
        TenantIntelligencePolicy.objects.create(
            tenant=self.tenant_a,
            strategy=TenantIntelligencePolicy.STRATEGY_BALANCED,
        )
        self._seed_common_customer_signals(self.tenant_a, self.agent_a)

        result = self._single_result_for_customer(self.tenant_a, self.agent_a)
        self.assertEqual(result["suggested_action"], "follow_up")

    def test_high_value_focus_strategy(self):
        TenantIntelligencePolicy.objects.create(
            tenant=self.tenant_a,
            strategy=TenantIntelligencePolicy.STRATEGY_HIGH_VALUE_FOCUS,
        )
        self._seed_common_customer_signals(self.tenant_a, self.agent_a)

        result = self._single_result_for_customer(self.tenant_a, self.agent_a)
        self.assertEqual(result["suggested_action"], "visit")

    def test_reactivation_focus_strategy(self):
        TenantIntelligencePolicy.objects.create(
            tenant=self.tenant_a,
            strategy=TenantIntelligencePolicy.STRATEGY_REACTIVATION_FOCUS,
        )
        self._seed_common_customer_signals(self.tenant_a, self.agent_a)

        result = self._single_result_for_customer(self.tenant_a, self.agent_a)
        self.assertEqual(result["suggested_action"], "reactivation_campaign")

    def test_same_signals_different_strategies_change_score_and_action(self):
        TenantIntelligencePolicy.objects.create(
            tenant=self.tenant_a,
            strategy=TenantIntelligencePolicy.STRATEGY_HIGH_VALUE_FOCUS,
        )
        TenantIntelligencePolicy.objects.create(
            tenant=self.tenant_b,
            strategy=TenantIntelligencePolicy.STRATEGY_REACTIVATION_FOCUS,
        )
        self._seed_common_customer_signals(self.tenant_a, self.agent_a, customer_id=500)
        self._seed_common_customer_signals(self.tenant_b, self.agent_b, customer_id=500)

        high_value_result = self._single_result_for_customer(
            self.tenant_a, self.agent_a, customer_id=500
        )
        reactivation_result = self._single_result_for_customer(
            self.tenant_b, self.agent_b, customer_id=500
        )

        self.assertNotEqual(high_value_result["score"], reactivation_result["score"])
        self.assertNotEqual(
            high_value_result["suggested_action"],
            reactivation_result["suggested_action"],
        )

    def test_tenant_isolation_policy_not_leaking(self):
        TenantIntelligencePolicy.objects.create(
            tenant=self.tenant_a,
            strategy=TenantIntelligencePolicy.STRATEGY_REACTIVATION_FOCUS,
        )
        self._seed_common_customer_signals(self.tenant_a, self.agent_a, customer_id=700)
        self._seed_common_customer_signals(self.tenant_b, self.agent_b, customer_id=700)

        tenant_a_result = self._single_result_for_customer(
            self.tenant_a, self.agent_a, customer_id=700
        )
        tenant_b_result = self._single_result_for_customer(
            self.tenant_b, self.agent_b, customer_id=700
        )

        self.assertEqual(tenant_a_result["suggested_action"], "reactivation_campaign")
        self.assertEqual(tenant_b_result["suggested_action"], "follow_up")
