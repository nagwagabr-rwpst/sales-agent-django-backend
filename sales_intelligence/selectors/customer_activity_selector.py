from django.db.models import Count, Max, Q

from odoo.models import OfflineSalesOrder


def get_customer_activity_summary(tenant, sales_agent):
    """
    Aggregate offline order activity per customer for one sales agent scope.
    """
    queryset = (
        OfflineSalesOrder.objects.filter(tenant=tenant, sales_agent=sales_agent)
        .values("customer_id")
        .annotate(
            total_orders=Count("id"),
            last_order_date=Max("created_at"),
            synced_orders_count=Count(
                "id", filter=Q(status=OfflineSalesOrder.STATUS_SYNCED)
            ),
            pending_orders_count=Count(
                "id", filter=Q(status=OfflineSalesOrder.STATUS_PENDING)
            ),
        )
    )
    return list(queryset)
