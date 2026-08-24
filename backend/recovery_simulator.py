import random


MAX_RECOVERY_ATTEMPTS = 3


def get_recovery_probability(score, action, failure_reason):
    """
    Estimate the probability that the recovery action
    will successfully recover the payment.
    """

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

    # Keep probability between 0 and 0.95
    probability = max(0.0, min(probability, 0.95))

    return round(probability, 2)


def check_stopping_rule(transaction, action):
    """
    Prevent excessive or inappropriate recovery attempts.
    """

    attempts = int(transaction.get("attempt_count", 0))

    # Successful payment should never be recovered again
    if transaction.get("status") == "SUCCESS":
        return False, "Payment already succeeded."

    # STOP action is always blocked
    if action == "STOP":
        return False, "AI decision is STOP; no recovery attempt allowed."

    # Maximum retry attempts
    if attempts >= MAX_RECOVERY_ATTEMPTS:
        return (
            False,
            f"Maximum recovery attempts ({MAX_RECOVERY_ATTEMPTS}) reached."
        )

    # Escalation is not an automated recovery attempt
    if action == "ESCALATE":
        return True, "Manual escalation permitted."

    return True, "Recovery action permitted."


def simulate_recovery(transaction, action, score):

    probability = get_recovery_probability(
        score,
        action,
        transaction["failure_reason"]
    )

    attempts_before = int(
        transaction.get("attempt_count", 0)
    )

    # Check stopping rules
    allowed, stopping_reason = check_stopping_rule(
        transaction,
        action
    )

    # Stopping rule blocked the action
    if not allowed:
        return {
            "recovery_probability": probability,
            "recovery_status": "STOPPED",
            "recovered_amount": 0,
            "attempts_before": attempts_before,
            "attempts_after": attempts_before,
            "action_executed": False,
            "stopping_rule": stopping_reason
        }

    # Escalation requires manual intervention
    if action == "ESCALATE":
        return {
            "recovery_probability": probability,
            "recovery_status": "ESCALATED",
            "recovered_amount": 0,
            "attempts_before": attempts_before,
            "attempts_after": attempts_before,
            "action_executed": True,
            "stopping_rule": (
                "Manual review required before further recovery."
            )
        }

    # REMIND does not count as a payment retry
    if action == "REMIND":
        return {
            "recovery_probability": probability,
            "recovery_status": "REMINDER_SENT",
            "recovered_amount": 0,
            "attempts_before": attempts_before,
            "attempts_after": attempts_before,
            "action_executed": True,
            "stopping_rule": (
                "Reminder sent; no additional payment attempt made."
            )
        }

    # RETRY counts as a recovery attempt
    attempts_after = attempts_before + 1

    random_value = random.random()

    # Recovery successful
    if random_value <= probability:
        return {
            "recovery_probability": probability,
            "recovery_status": "RECOVERED",
            "recovered_amount": transaction["amount"],
            "attempts_before": attempts_before,
            "attempts_after": attempts_after,
            "action_executed": True,
            "stopping_rule": (
                "Recovery succeeded; further attempts stopped."
            )
        }

    # Retry failed
    if attempts_after >= MAX_RECOVERY_ATTEMPTS:
        next_status = "STOPPED"

        rule = (
            f"Maximum recovery attempts ({MAX_RECOVERY_ATTEMPTS}) "
            "reached after failed retry."
        )

    else:
        next_status = "FAILED"

        rule = (
            f"Retry failed. "
            f"{MAX_RECOVERY_ATTEMPTS - attempts_after} "
            "attempt(s) remaining."
        )

    return {
        "recovery_probability": probability,
        "recovery_status": next_status,
        "recovered_amount": 0,
        "attempts_before": attempts_before,
        "attempts_after": attempts_after,
        "action_executed": True,
        "stopping_rule": rule
    }