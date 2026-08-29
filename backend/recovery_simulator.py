
import random


# ============================================================
# REVORA - RECOVERY SIMULATOR
# ============================================================

MAX_RECOVERY_ATTEMPTS = 3


# ============================================================
# RECOVERY PROBABILITY
# ============================================================

def get_recovery_probability(score, action, failure_reason):
    """
    Estimate recovery probability based on
    score, action and failure reason.
    """

    failure_reason = str(failure_reason).upper()

    # Base probability from recovery score

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
        probability = 0.0

    elif action == "STOP":
        return 0.0

    # Failure adjustment

    if failure_reason == "NETWORK_ERROR":
        probability += 0.05

    elif failure_reason == "CARD_EXPIRED":
        probability -= 0.15

    elif failure_reason == "BANK_DECLINE":
        probability -= 0.05

    elif failure_reason == "UNKNOWN":
        probability -= 0.05

    probability = max(
        0.0,
        min(probability, 0.95)
    )

    return round(probability, 2)


# ============================================================
# STOPPING RULE ENGINE
# ============================================================

def check_stopping_rule(transaction, action):
    """
    Apply bounded recovery workflow rules.
    """

    attempts = int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    status = str(
        transaction.get(
            "status",
            ""
        )
    ).upper()

    # Payment already successful

    if status == "SUCCESS":
        return (
            False,
            "Payment already succeeded."
        )

    # STOP is intentionally blocked

    if action == "STOP":
        return (
            False,
            "AI decision is STOP; no recovery action allowed."
        )

    # IMPORTANT:
    # ESCALATE must be allowed even after max attempts.
    # It is NOT another retry.
    # It represents manual review.

    if action == "ESCALATE":
        return (
            True,
            "Manual escalation permitted."
        )

    # REMIND does not increase attempts

    if action == "REMIND":
        return (
            True,
            "Customer reminder permitted."
        )

    # RETRY obeys maximum retry rule

    if action == "RETRY":

        if attempts >= MAX_RECOVERY_ATTEMPTS:
            return (
                False,
                f"Maximum recovery attempts ({MAX_RECOVERY_ATTEMPTS}) reached."
            )

        return (
            True,
            "Recovery retry permitted."
        )

    return (
        False,
        "Unsupported recovery action."
    )


# ============================================================
# SIMULATE RECOVERY
# ============================================================

def simulate_recovery(transaction, action, score):

    failure_reason = str(
        transaction.get(
            "failure_reason",
            "UNKNOWN"
        )
    ).upper()

    probability = get_recovery_probability(
        score,
        action,
        failure_reason
    )

    attempts_before = int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    # --------------------------------------------------------
    # CHECK STOPPING RULE
    # --------------------------------------------------------

    allowed, stopping_reason = check_stopping_rule(
        transaction,
        action
    )

    if not allowed:

        return {

            "recovery_probability":
                probability,

            "recovery_status":
                "STOPPED",

            "recovered_amount":
                0,

            "attempts_before":
                attempts_before,

            "attempts_after":
                attempts_before,

            "action_executed":
                False,

            "stopping_rule":
                stopping_reason
        }

    # --------------------------------------------------------
    # ESCALATE
    # --------------------------------------------------------

    if action == "ESCALATE":

        return {

            "recovery_probability":
                0.0,

            "recovery_status":
                "ESCALATED",

            "recovered_amount":
                0,

            "attempts_before":
                attempts_before,

            "attempts_after":
                attempts_before,

            "action_executed":
                True,

            "stopping_rule":
                (
                    "Automated recovery stopped. "
                    "Transaction escalated for manual review."
                )
        }

    # --------------------------------------------------------
    # REMIND
    # --------------------------------------------------------

    if action == "REMIND":

        return {

            "recovery_probability":
                probability,

            "recovery_status":
                "REMINDER_SENT",

            "recovered_amount":
                0,

            "attempts_before":
                attempts_before,

            "attempts_after":
                attempts_before,

            "action_executed":
                True,

            "stopping_rule":
                (
                    "Reminder sent; no payment retry performed."
                )
        }

    # --------------------------------------------------------
    # RETRY
    # --------------------------------------------------------

    attempts_after = attempts_before + 1

    random_value = random.random()

    # Successful recovery

    if random_value <= probability:

        return {

            "recovery_probability":
                probability,

            "recovery_status":
                "RECOVERED",

            "recovered_amount":
                float(
                    transaction.get(
                        "amount",
                        0
                    )
                ),

            "attempts_before":
                attempts_before,

            "attempts_after":
                attempts_after,

            "action_executed":
                True,

            "stopping_rule":
                (
                    "Recovery succeeded; further attempts stopped."
                )
        }

    # --------------------------------------------------------
    # RETRY FAILED
    # --------------------------------------------------------

    if attempts_after >= MAX_RECOVERY_ATTEMPTS:

        return {

            "recovery_probability":
                probability,

            "recovery_status":
                "STOPPED",

            "recovered_amount":
                0,

            "attempts_before":
                attempts_before,

            "attempts_after":
                attempts_after,

            "action_executed":
                True,

            "stopping_rule":
                (
                    f"Maximum recovery attempts ({MAX_RECOVERY_ATTEMPTS}) "
                    "reached after failed retry."
                )
        }

    return {

        "recovery_probability":
            probability,

        "recovery_status":
            "FAILED",

        "recovered_amount":
            0,

        "attempts_before":
            attempts_before,

        "attempts_after":
            attempts_after,

        "action_executed":
            True,

        "stopping_rule":
            (
                f"Retry failed. "
                f"{MAX_RECOVERY_ATTEMPTS - attempts_after} "
                "attempt(s) remaining."
            )
    }