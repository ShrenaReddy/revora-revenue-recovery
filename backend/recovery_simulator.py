import random


def get_recovery_probability(score, action, failure_reason):
    # Base probability based on recovery score
    if score >= 70:
        probability = 0.80
    elif score >= 40:
        probability = 0.55
    else:
        probability = 0.20

    # Action adjustment
    if action == "RETRY":
        probability += 0.10

    elif action == "REMIND":
        probability += 0.05

    elif action == "ESCALATE":
        probability += 0.15

    elif action == "STOP":
        return 0.0

    # Failure-specific adjustment
    if failure_reason == "NETWORK_ERROR":
        probability += 0.05

    elif failure_reason == "CARD_EXPIRED":
        probability -= 0.15

    elif failure_reason == "BANK_DECLINE":
        probability -= 0.05

    elif failure_reason == "UNKNOWN":
        probability -= 0.05

    # Keep probability between 0 and 1
    probability = max(0.0, min(probability, 0.95))

    return round(probability, 2)


def simulate_recovery(transaction, action, score):

    probability = get_recovery_probability(
        score,
        action,
        transaction["failure_reason"]
    )

    # No recovery attempt
    if action == "STOP":
        return {
            "recovery_probability": probability,
            "recovery_status": "STOPPED",
            "recovered_amount": 0
        }

    # Escalation requires manual intervention
    if action == "ESCALATE":
        return {
            "recovery_probability": probability,
            "recovery_status": "ESCALATED",
            "recovered_amount": 0
        }

    # Simulate recovery
    random_value = random.random()

    if random_value <= probability:
        return {
            "recovery_probability": probability,
            "recovery_status": "RECOVERED",
            "recovered_amount": transaction["amount"]
        }

    return {
        "recovery_probability": probability,
        "recovery_status": "FAILED",
        "recovered_amount": 0
    }