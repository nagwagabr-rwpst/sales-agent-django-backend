STRATEGY_BALANCED = "balanced"
STRATEGY_HIGH_VALUE_FOCUS = "high_value_focus"
STRATEGY_REACTIVATION_FOCUS = "reactivation_focus"


STRATEGY_PROFILES = {
    STRATEGY_BALANCED: {
        "recency_weight": 1.0,
        "volume_weight": 1.0,
        "pending_weight": 1.0,
        "inactivity_weight": 1.0,
    },
    STRATEGY_HIGH_VALUE_FOCUS: {
        "recency_weight": 0.9,
        "volume_weight": 1.4,
        "pending_weight": 1.1,
        "inactivity_weight": 0.6,
    },
    STRATEGY_REACTIVATION_FOCUS: {
        "recency_weight": 0.7,
        "volume_weight": 0.8,
        "pending_weight": 1.0,
        "inactivity_weight": 1.8,
    },
}

