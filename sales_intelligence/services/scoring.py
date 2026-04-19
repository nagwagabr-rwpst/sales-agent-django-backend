from django.utils import timezone


def calculate_customer_score(summary):
    """
    Simple deterministic MVP scoring:
    - Recent activity gets more points
    - Higher order volume gets more points
    - Pending orders slightly increase urgency
    """
    total_orders = summary.get("total_orders", 0) or 0
    pending_orders = summary.get("pending_orders_count", 0) or 0
    last_order_date = summary.get("last_order_date")

    if last_order_date is None:
        recency_points = 0.0
    else:
        age_days = max((timezone.now() - last_order_date).days, 0)
        recency_points = max(0.0, 50.0 - min(age_days, 50))

    volume_points = min(float(total_orders) * 8.0, 35.0)
    pending_points = min(float(pending_orders) * 3.0, 15.0)

    score = round(recency_points + volume_points + pending_points, 2)

    if score >= 70:
        priority_level = "high"
    elif score >= 40:
        priority_level = "medium"
    else:
        priority_level = "low"

    return {
        "score": score,
        "priority_level": priority_level,
    }
