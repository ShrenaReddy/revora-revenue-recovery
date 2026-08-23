def calculate_recovery_score(transaction):
    score = 0

    # Customer history
    score += transaction["previous_success_rate"] * 40

    # Transaction amount
    amount = transaction["amount"]

    if amount < 5000:
        score += 20
    elif amount < 20000:
        score += 15
    elif amount < 50000:
        score += 10
    else:
        score += 5

    # Previous attempts
    attempts = transaction["attempt_count"]

    if attempts == 1:
        score += 20
    elif attempts == 2:
        score += 10

    # Customer type
    if transaction["customer_type"] == "RETURNING":
        score += 10
    else:
        score += 5

    return round(min(score, 100), 2)


def get_risk_level(score):
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


def determine_action(transaction, score):
    status = transaction["status"]
    failure = transaction["failure_reason"]
    risk = get_risk_level(score)

    # Successful payments don't need recovery
    if status == "SUCCESS":
        return "STOP"

    # Abandoned payments
    if status == "ABANDONED":
        if risk == "HIGH":
            return "REMIND"
        else:
            return "STOP"

    # Failed payments
    if failure == "INSUFFICIENT_FUNDS":
        if risk == "HIGH":
            return "RETRY"
        elif risk == "MEDIUM":
            return "REMIND"
        else:
            return "STOP"

    if failure == "NETWORK_ERROR":
        if risk in ["HIGH", "MEDIUM"]:
            return "RETRY"
        else:
            return "STOP"

    if failure == "BANK_DECLINE":
        if risk in ["HIGH", "MEDIUM"]:
            return "REMIND"
        else:
            return "STOP"

    if failure == "CARD_EXPIRED":
        return "REMIND"

    if failure == "LIMIT_EXCEEDED":
        if risk in ["HIGH", "MEDIUM"]:
            return "REMIND"
        else:
            return "STOP"

    if failure == "UNKNOWN":
        if risk in ["HIGH", "MEDIUM"]:
            return "ESCALATE"
        else:
            return "STOP"

    return "STOP"


def generate_reason(transaction, score, action):
    failure = transaction["failure_reason"]
    risk = get_risk_level(score)

    if action == "RETRY":
        return f"{risk} recovery potential and {failure.lower().replace('_', ' ')} is suitable for retry."

    if action == "REMIND":
        return f"{risk} recovery potential; customer should be reminded to complete payment."

    if action == "ESCALATE":
        return "Failure reason is uncertain and requires further investigation."

    if action == "STOP":
        if transaction["status"] == "SUCCESS":
            return "Payment already succeeded; no recovery action required."

        return "Low recovery potential or further recovery attempts are not recommended."

    return "No action required."


def analyze_transaction(transaction):
    score = calculate_recovery_score(transaction)

    risk = get_risk_level(score)

    action = determine_action(transaction, score)

    reason = generate_reason(
        transaction,
        score,
        action
    )

    return {
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["amount"],
        "status": transaction["status"],
        "failure_reason": transaction["failure_reason"],
        "recovery_score": score,
        "risk_level": risk,
        "recommended_action": action,
        "decision_reason": reason
    }