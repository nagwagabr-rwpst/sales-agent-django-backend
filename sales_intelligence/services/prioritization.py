from django.utils import timezone

from sales_intelligence.selectors.customer_activity_selector import (
    get_customer_activity_summary,
)
from sales_intelligence.services.scoring import calculate_customer_score


def _get_suggested_action(summary):
    total_orders = summary.get("total_orders", 0) or 0
    last_order_date = summary.get("last_order_date")

    if total_orders == 0:
        return "visit"

    if last_order_date is None:
        return "visit"

    age_days = max((timezone.now() - last_order_date).days, 0)
    if age_days > 30:
        return "follow_up"

    if total_orders >= 5 and age_days <= 14:
        return "low_priority"

    return "visit"


def get_prioritized_customers(tenant, sales_agent):
    customer_summaries = get_customer_activity_summary(tenant, sales_agent)

    results = []
    for summary in customer_summaries:
        scoring = calculate_customer_score(summary)
        results.append(
            {
                "customer_id": summary["customer_id"],
                "score": scoring["score"],
                "priority_level": scoring["priority_level"],
                "suggested_action": _get_suggested_action(summary),
            }
        )

    return sorted(results, key=lambda row: row["score"], reverse=True)
