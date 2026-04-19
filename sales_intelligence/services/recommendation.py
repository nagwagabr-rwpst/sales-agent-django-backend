from django.utils import timezone

from sales_intelligence.services.strategy_profiles import (
    STRATEGY_BALANCED,
    STRATEGY_HIGH_VALUE_FOCUS,
    STRATEGY_REACTIVATION_FOCUS,
)


def get_suggested_action(summary, strategy=STRATEGY_BALANCED):
    total_orders = summary.get("total_orders", 0) or 0
    last_order_date = summary.get("last_order_date")

    if last_order_date is None:
        age_days = 120
    else:
        age_days = max((timezone.now() - last_order_date).days, 0)

    if strategy == STRATEGY_HIGH_VALUE_FOCUS:
        if total_orders >= 8 and age_days <= 21:
            return "priority_sales_outreach"
        if total_orders >= 5 and age_days > 21:
            return "executive_follow_up"
        # Keep high-value candidates in proactive outreach instead of generic follow-up.
        if total_orders >= 3 and age_days > 30:
            return "visit"
        if age_days > 45:
            return "follow_up"
        return "visit"

    if strategy == STRATEGY_REACTIVATION_FOCUS:
        if total_orders >= 3 and age_days > 45:
            return "reactivation_campaign"
        if age_days > 30:
            return "personal_check_in"
        if age_days <= 14:
            return "low_priority"
        return "follow_up"

    if total_orders == 0:
        return "visit"
    if age_days > 30:
        return "follow_up"
    if total_orders >= 5 and age_days <= 14:
        return "low_priority"
    return "visit"

