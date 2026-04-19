from sales_intelligence.selectors.customer_activity_selector import (
    get_customer_activity_summary,
)
from sales_intelligence.services.intelligence_policy import (
    get_tenant_intelligence_strategy,
)
from sales_intelligence.services.recommendation import get_suggested_action
from sales_intelligence.services.scoring import calculate_customer_score


def get_prioritized_customers(tenant, sales_agent):
    strategy = get_tenant_intelligence_strategy(tenant)
    customer_summaries = get_customer_activity_summary(tenant, sales_agent)

    results = []
    for summary in customer_summaries:
        scoring = calculate_customer_score(summary, strategy=strategy)
        results.append(
            {
                "customer_id": summary["customer_id"],
                "score": scoring["score"],
                "priority_level": scoring["priority_level"],
                "suggested_action": get_suggested_action(summary, strategy=strategy),
            }
        )

    return sorted(results, key=lambda row: row["score"], reverse=True)
