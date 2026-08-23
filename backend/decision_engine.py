def calculate_recovery_score(transaction):
    score = 0

    # Customer history
    previous_success_rate = float(
        transaction.get("previous_success_rate", 0)
    )

    customer_history_score = previous_success_rate * 40
    score += customer_history_score

    # Transaction amount
    amount = float(transaction.get("amount", 0))

    if amount < 5000:
        amount_score = 20
    elif amount < 20000:
        amount_score = 15
    elif amount < 50000:
        amount_score = 10
    else:
        amount_score = 5

    score += amount_score

    # Previous attempts
    attempts = int(transaction.get("attempt_count", 0))

    if attempts == 1:
        attempt_score = 20
    elif attempts == 2:
        attempt_score = 10
    else:
        attempt_score = 0

    score += attempt_score

    # Customer type
    customer_type = transaction.get("customer_type", "")

    if customer_type == "RETURNING":
        customer_type_score = 10
    else:
        customer_type_score = 5

    score += customer_type_score

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
    """
    Generate an explainable recovery decision.

    The explanation is based directly on the factors
    used by Revora's recovery scoring and decision engine.
    """

    risk = get_risk_level(score)

    failure = transaction.get(
        "failure_reason",
        "UNKNOWN"
    )

    failure_text = failure.replace(
        "_",
        " "
    ).lower()

    previous_success_rate = float(
        transaction.get(
            "previous_success_rate",
            0
        )
    )

    attempts = int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    amount = float(
        transaction.get(
            "amount",
            0
        )
    )

    customer_type = transaction.get(
        "customer_type",
        "UNKNOWN"
    )

    # -----------------------------
    # Explain customer history
    # -----------------------------

    if previous_success_rate >= 0.75:
        history_reason = (
            f"strong historical payment success rate "
            f"({previous_success_rate * 100:.0f}%)"
        )

    elif previous_success_rate >= 0.50:
        history_reason = (
            f"moderate historical payment success rate "
            f"({previous_success_rate * 100:.0f}%)"
        )

    else:
        history_reason = (
            f"low historical payment success rate "
            f"({previous_success_rate * 100:.0f}%)"
        )

    # -----------------------------
    # Explain retry attempts
    # -----------------------------

    if attempts == 0:
        attempt_reason = (
            "no previous recovery attempts have been made"
        )

    elif attempts == 1:
        attempt_reason = (
            "only one recovery attempt has been made"
        )

    elif attempts == 2:
        attempt_reason = (
            "two recovery attempts have already been made"
        )

    else:
        attempt_reason = (
            f"{attempts} recovery attempts have already been made"
        )

    # -----------------------------
    # Explain customer type
    # -----------------------------

    if customer_type == "RETURNING":
        customer_reason = (
            "the customer is a returning customer"
        )
    else:
        customer_reason = (
            "the customer is not classified as returning"
        )

    # -----------------------------
    # Explain transaction value
    # -----------------------------

    amount_reason = (
        f"transaction value is ₹{amount:,.2f}"
    )

    # -----------------------------
    # Action-specific explanation
    # -----------------------------

    if action == "RETRY":

        return (
            f"{risk} recovery potential because of "
            f"{history_reason}, {attempt_reason}, and "
            f"a recoverable {failure_text} failure. "
            f"{customer_reason}. "
            f"{amount_reason}. "
            f"These factors support another payment retry."
        )

    if action == "REMIND":

        return (
            f"{risk} recovery potential with "
            f"{history_reason}. "
            f"The payment failure is {failure_text}. "
            f"{attempt_reason}. "
            f"{customer_reason}. "
            f"A customer reminder is recommended before "
            f"another payment attempt."
        )

    if action == "ESCALATE":

        return (
            f"{risk} recovery potential, but the "
            f"{failure_text} failure requires additional "
            f"investigation. "
            f"{attempt_reason}. "
            f"{customer_reason}. "
            f"Revora recommends escalation instead of "
            f"an automated retry."
        )

    if action == "STOP":

        if transaction.get("status") == "SUCCESS":
            return (
                "Payment already succeeded. "
                "Revora stops the recovery workflow because "
                "no further action is required."
            )

        return (
            f"{risk} recovery potential with "
            f"{history_reason}. "
            f"{attempt_reason}. "
            f"The {failure_text} failure does not meet "
            f"Revora's recovery criteria. "
            f"Further automated recovery is therefore stopped."
        )

    return "No recovery action required."


def generate_decision_factors(transaction, score, action):
    """
    Return structured factors used to explain
    the recovery decision.
    """

    previous_success_rate = float(
        transaction.get(
            "previous_success_rate",
            0
        )
    )

    attempts = int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    customer_type = transaction.get(
        "customer_type",
        "UNKNOWN"
    )

    failure = transaction.get(
        "failure_reason",
        "UNKNOWN"
    )

    risk = get_risk_level(score)

    factors = []

    factors.append({
        "factor": "Recovery Score",
        "value": f"{score:.1f}/100",
        "impact": risk
    })

    factors.append({
        "factor": "Previous Success Rate",
        "value": f"{previous_success_rate * 100:.0f}%",
        "impact": (
            "POSITIVE"
            if previous_success_rate >= 0.5
            else "NEGATIVE"
        )
    })

    factors.append({
        "factor": "Previous Attempts",
        "value": str(attempts),
        "impact": (
            "POSITIVE"
            if attempts <= 1
            else "CAUTION"
        )
    })

    factors.append({
        "factor": "Customer Type",
        "value": customer_type,
        "impact": (
            "POSITIVE"
            if customer_type == "RETURNING"
            else "NEUTRAL"
        )
    })

    factors.append({
        "factor": "Failure Reason",
        "value": failure.replace("_", " "),
        "impact": "DECISION INPUT"
    })

    factors.append({
        "factor": "Recommended Action",
        "value": action,
        "impact": "AI DECISION"
    })

    return factors


def analyze_transaction(transaction):

    score = calculate_recovery_score(
        transaction
    )

    risk = get_risk_level(score)

    action = determine_action(
        transaction,
        score
    )

    reason = generate_reason(
        transaction,
        score,
        action
    )

    decision_factors = generate_decision_factors(
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

        "decision_reason": reason,

        "decision_factors": decision_factors
    }