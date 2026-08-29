# ============================================================
# REVORA - AI RECOVERY DECISION ENGINE
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

MAX_RECOVERY_ATTEMPTS = 3


# ============================================================
# CALCULATE RECOVERY SCORE
# ============================================================

def calculate_recovery_score(transaction):
    """
    Calculate a bounded recovery score from 0-100.

    Factors:
    - Previous payment success rate
    - Transaction amount
    - Previous recovery attempts
    - Customer type
    """

    score = 0

    # --------------------------------------------------------
    # 1. Customer payment history
    # --------------------------------------------------------

    previous_success_rate = float(
        transaction.get(
            "previous_success_rate",
            0
        )
    )

    # Support both:
    # 0.83 -> 83%
    # 83   -> 83%

    if previous_success_rate > 1:
        previous_success_rate /= 100

    previous_success_rate = max(
        0,
        min(previous_success_rate, 1)
    )

    customer_history_score = (
        previous_success_rate * 40
    )

    score += customer_history_score

    # --------------------------------------------------------
    # 2. Transaction amount
    # --------------------------------------------------------

    amount = float(
        transaction.get(
            "amount",
            0
        )
    )

    if amount < 5000:
        amount_score = 20

    elif amount < 20000:
        amount_score = 15

    elif amount < 50000:
        amount_score = 10

    else:
        amount_score = 5

    score += amount_score

    # --------------------------------------------------------
    # 3. Previous recovery attempts
    # --------------------------------------------------------

    attempts = int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    if attempts == 0:
        attempt_score = 20

    elif attempts == 1:
        attempt_score = 20

    elif attempts == 2:
        attempt_score = 10

    else:
        attempt_score = 0

    score += attempt_score

    # --------------------------------------------------------
    # 4. Customer type
    # --------------------------------------------------------

    customer_type = str(
        transaction.get(
            "customer_type",
            ""
        )
    ).upper()

    if customer_type == "RETURNING":
        customer_type_score = 10
    else:
        customer_type_score = 5

    score += customer_type_score

    # --------------------------------------------------------
    # Final bounded score
    # --------------------------------------------------------

    return round(
        min(score, 100),
        2
    )


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# DETERMINE RECOVERY ACTION
# ============================================================

def determine_action(transaction, score):
    """
    Determine the safest recovery action.

    Possible actions:
    - RETRY
    - REMIND
    - ESCALATE
    - STOP

    ESCALATE means the transaction requires human review
    before additional recovery action.
    """

    status = str(
        transaction.get(
            "status",
            ""
        )
    ).upper()

    failure = str(
        transaction.get(
            "failure_reason",
            "UNKNOWN"
        )
    ).upper()

    risk = get_risk_level(score)

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

    # --------------------------------------------------------
    # 1. Successful payment
    # --------------------------------------------------------

    if status == "SUCCESS":
        return "STOP"

    # --------------------------------------------------------
    # 2. Maximum automated attempts reached
    #
    # Never continue automated recovery after the limit.
    # Send the transaction for manual review.
    # --------------------------------------------------------

    if attempts >= MAX_RECOVERY_ATTEMPTS:
        return "ESCALATE"

    # --------------------------------------------------------
    # 3. Unknown failure
    #
    # Unknown failures should not be blindly retried.
    # Human review is appropriate when there is meaningful
    # recovery potential.
    # --------------------------------------------------------

    if failure == "UNKNOWN":

        if score >= 40:
            return "ESCALATE"

        return "STOP"

    # --------------------------------------------------------
    # 4. Abandoned payment
    # --------------------------------------------------------

    if status == "ABANDONED":

        if risk == "HIGH":
            return "REMIND"

        elif risk == "MEDIUM":
            return "REMIND"

        return "STOP"

    # --------------------------------------------------------
    # 5. Insufficient funds
    # --------------------------------------------------------

    if failure == "INSUFFICIENT_FUNDS":

        # Very strong customer/payment history:
        # controlled retry is reasonable.
        if risk == "HIGH":
            return "RETRY"

        # Medium-confidence cases should first receive
        # a reminder rather than an automatic payment attempt.
        elif risk == "MEDIUM":
            return "REMIND"

        return "STOP"

    # --------------------------------------------------------
    # 6. Network error
    # --------------------------------------------------------

    if failure == "NETWORK_ERROR":

        if risk == "HIGH":
            return "RETRY"

        elif risk == "MEDIUM":
            return "RETRY"

        # Low-confidence network failures can be escalated
        # when the transaction has meaningful value.
        if amount >= 20000:
            return "ESCALATE"

        return "STOP"

    # --------------------------------------------------------
    # 7. Bank decline
    #
    # Bank declines can have external causes and should not
    # always be repeatedly retried.
    # --------------------------------------------------------

    if failure == "BANK_DECLINE":

        # High-risk bank declines are sent for manual review.
        if risk == "HIGH":
            return "ESCALATE"

        # Medium-risk cases receive a reminder first.
        elif risk == "MEDIUM":
            return "REMIND"

        # High-value low-risk transactions deserve review
        # instead of silently stopping.
        elif amount >= 50000:
            return "ESCALATE"

        return "STOP"

    # --------------------------------------------------------
    # 8. Card expired
    # --------------------------------------------------------

    if failure == "CARD_EXPIRED":

        # Expired cards should not be automatically retried.
        # Customer needs to update payment information.
        if amount >= 50000 and risk in ["HIGH", "MEDIUM"]:
            return "ESCALATE"

        return "REMIND"

    # --------------------------------------------------------
    # 9. Limit exceeded
    # --------------------------------------------------------

    if failure == "LIMIT_EXCEEDED":

        if risk == "HIGH":
            return "ESCALATE"

        elif risk == "MEDIUM":
            return "REMIND"

        return "STOP"

    # --------------------------------------------------------
    # 10. High-value unknown/other failures
    #
    # Protect against blindly recovering large-value payments.
    # --------------------------------------------------------

    if amount >= 50000:

        if risk in ["HIGH", "MEDIUM"]:
            return "ESCALATE"

    # --------------------------------------------------------
    # 11. Default
    # --------------------------------------------------------

    return "STOP"


# ============================================================
# GENERATE EXPLAINABLE DECISION REASON
# ============================================================

def generate_reason(
    transaction,
    score,
    action
):

    risk = get_risk_level(score)

    status = str(
        transaction.get(
            "status",
            ""
        )
    ).upper()

    failure = str(
        transaction.get(
            "failure_reason",
            "UNKNOWN"
        )
    ).upper()

    previous_success_rate = float(
        transaction.get(
            "previous_success_rate",
            0
        )
    )

    if previous_success_rate > 1:
        previous_success_rate /= 100

    previous_success_rate = max(
        0,
        min(previous_success_rate, 1)
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

    customer_type = str(
        transaction.get(
            "customer_type",
            "UNKNOWN"
        )
    ).upper()

    # --------------------------------------------------------
    # History explanation
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Attempt explanation
    # --------------------------------------------------------

    if attempts == 0:

        attempt_reason = (
            "no previous recovery attempts have been made"
        )

    elif attempts == 1:

        attempt_reason = (
            "one previous recovery attempt has been made"
        )

    elif attempts == 2:

        attempt_reason = (
            "two previous recovery attempts have been made"
        )

    else:

        attempt_reason = (
            f"{attempts} previous recovery attempts have "
            f"already been made"
        )

    # --------------------------------------------------------
    # Customer type explanation
    # --------------------------------------------------------

    if customer_type == "RETURNING":

        customer_reason = (
            "the customer is a returning customer"
        )

    elif customer_type == "NEW":

        customer_reason = (
            "the customer is classified as a new customer"
        )

    else:

        customer_reason = (
            "the customer type is not classified as returning"
        )

    # --------------------------------------------------------
    # Amount explanation
    # --------------------------------------------------------

    if amount < 5000:

        amount_reason = (
            f"the transaction value is ₹{amount:,.2f}, "
            f"which receives a higher recovery priority"
        )

    elif amount < 20000:

        amount_reason = (
            f"the transaction value is ₹{amount:,.2f}, "
            f"which receives a moderate recovery priority"
        )

    elif amount < 50000:

        amount_reason = (
            f"the transaction value is ₹{amount:,.2f}, "
            f"which receives a lower recovery priority"
        )

    else:

        amount_reason = (
            f"the transaction value is ₹{amount:,.2f}, "
            f"which receives a conservative recovery priority"
        )

    failure_text = failure.replace(
        "_",
        " "
    ).lower()

    # --------------------------------------------------------
    # SUCCESS / STOP
    # --------------------------------------------------------

    if action == "STOP":

        if status == "SUCCESS":

            return (
                "Payment already succeeded. "
                "Revora stops the recovery workflow because "
                "no further action is required."
            )

        return (
            f"{risk} recovery potential based on "
            f"{history_reason}. "
            f"{attempt_reason}. "
            f"The {failure_text} failure does not meet "
            f"Revora's automated recovery criteria. "
            f"{customer_reason}. "
            f"{amount_reason}. "
            f"Further automated recovery is therefore stopped."
        )

    # --------------------------------------------------------
    # RETRY
    # --------------------------------------------------------

    if action == "RETRY":

        if failure == "NETWORK_ERROR":

            return (
                f"{risk} recovery potential driven by "
                f"{history_reason}. "
                f"{attempt_reason}. "
                f"The network error is considered recoverable "
                f"through another controlled payment attempt. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora recommends a controlled retry."
            )

        if failure == "INSUFFICIENT_FUNDS":

            return (
                f"{risk} recovery potential driven by "
                f"{history_reason}. "
                f"{attempt_reason}. "
                f"The insufficient-funds failure may be recoverable "
                f"through another controlled payment attempt. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora recommends a controlled retry."
            )

        return (
            f"{risk} recovery potential based on "
            f"{history_reason}. "
            f"{attempt_reason}. "
            f"The {failure_text} failure may be recoverable. "
            f"{customer_reason}. "
            f"{amount_reason}. "
            f"Revora recommends a controlled retry."
        )

    # --------------------------------------------------------
    # REMIND
    # --------------------------------------------------------

    if action == "REMIND":

        return (
            f"{risk} recovery potential with "
            f"{history_reason}. "
            f"The payment failure is {failure_text}. "
            f"{attempt_reason}. "
            f"{customer_reason}. "
            f"{amount_reason}. "
            f"Revora recommends a customer reminder "
            f"before another automated payment attempt."
        )

    # --------------------------------------------------------
    # ESCALATE
    # --------------------------------------------------------

    if action == "ESCALATE":

        # Maximum attempts
        if attempts >= MAX_RECOVERY_ATTEMPTS:

            return (
                f"{risk} recovery potential, but "
                f"{attempt_reason}. "
                f"Revora's safety policy prevents further "
                f"automated recovery attempts. "
                f"The {failure_text} failure requires "
                f"manual investigation. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora recommends escalation for manual review."
            )

        # Unknown failure
        if failure == "UNKNOWN":

            return (
                f"{risk} recovery potential based on "
                f"{history_reason}. "
                f"The failure reason is unknown and cannot be "
                f"safely handled by an automated recovery rule. "
                f"{attempt_reason}. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora escalates the transaction for manual "
                f"investigation before further recovery."
            )

        # Bank decline
        if failure == "BANK_DECLINE":

            return (
                f"{risk} recovery potential with "
                f"{history_reason}. "
                f"The bank-decline failure may require "
                f"additional investigation before another "
                f"payment attempt. "
                f"{attempt_reason}. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora recommends manual review instead of "
                f"blindly retrying the payment."
            )

        # Card expired
        if failure == "CARD_EXPIRED":

            return (
                f"{risk} recovery potential with "
                f"{history_reason}. "
                f"The card has expired and cannot be safely "
                f"retried without updated payment information. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora escalates this high-value case for "
                f"manual review."
            )

        # Limit exceeded
        if failure == "LIMIT_EXCEEDED":

            return (
                f"{risk} recovery potential with "
                f"{history_reason}. "
                f"The payment limit has been exceeded, so "
                f"another automated attempt may be inappropriate. "
                f"{attempt_reason}. "
                f"{customer_reason}. "
                f"{amount_reason}. "
                f"Revora recommends manual review before "
                f"further recovery."
            )

        # High-value transaction
        if amount >= 50000:

            return (
                f"{risk} recovery potential for a high-value "
                f"transaction of ₹{amount:,.2f}. "
                f"The {failure_text} failure requires additional "
                f"review before automated recovery continues. "
                f"{attempt_reason}. "
                f"{customer_reason}. "
                f"Revora recommends escalation to protect "
                f"against inappropriate automated recovery."
            )

        # General escalation
        return (
            f"{risk} recovery potential, but the "
            f"{failure_text} failure requires additional "
            f"investigation. "
            f"{attempt_reason}. "
            f"{customer_reason}. "
            f"{amount_reason}. "
            f"Revora recommends escalation instead of "
            f"another automated retry. "
            f"Manual review is required before further "
            f"recovery action."
        )

    return "No automated recovery action is required."


# ============================================================
# DECISION FACTORS
# ============================================================

def generate_decision_factors(
    transaction,
    score,
    action
):

    previous_success_rate = float(
        transaction.get(
            "previous_success_rate",
            0
        )
    )

    if previous_success_rate > 1:
        previous_success_rate /= 100

    attempts = int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    customer_type = str(
        transaction.get(
            "customer_type",
            "UNKNOWN"
        )
    ).upper()

    failure = str(
        transaction.get(
            "failure_reason",
            "UNKNOWN"
        )
    ).upper()

    amount = float(
        transaction.get(
            "amount",
            0
        )
    )

    risk = get_risk_level(
        score
    )

    factors = []

    # --------------------------------------------------------
    # Recovery score
    # --------------------------------------------------------

    factors.append({
        "factor": "Recovery Score",
        "value": f"{score:.1f}/100",
        "impact": risk
    })

    # --------------------------------------------------------
    # Historical success rate
    # --------------------------------------------------------

    factors.append({
        "factor": "Previous Success Rate",
        "value": (
            f"{previous_success_rate * 100:.0f}%"
        ),
        "impact": (
            "POSITIVE"
            if previous_success_rate >= 0.50
            else "NEGATIVE"
        )
    })

    # --------------------------------------------------------
    # Previous attempts
    # --------------------------------------------------------

    factors.append({
        "factor": "Previous Attempts",
        "value": str(attempts),
        "impact": (
            "POSITIVE"
            if attempts <= 1
            else "CAUTION"
        )
    })

    # --------------------------------------------------------
    # Customer type
    # --------------------------------------------------------

    factors.append({
        "factor": "Customer Type",
        "value": customer_type,
        "impact": (
            "POSITIVE"
            if customer_type == "RETURNING"
            else "NEUTRAL"
        )
    })

    # --------------------------------------------------------
    # Transaction amount
    # --------------------------------------------------------

    if amount < 5000:
        amount_impact = "HIGH PRIORITY"

    elif amount < 20000:
        amount_impact = "MEDIUM PRIORITY"

    elif amount < 50000:
        amount_impact = "LOWER PRIORITY"

    else:
        amount_impact = "CONSERVATIVE"

    factors.append({
        "factor": "Transaction Amount",
        "value": f"₹{amount:,.2f}",
        "impact": amount_impact
    })

    # --------------------------------------------------------
    # Failure reason
    # --------------------------------------------------------

    factors.append({
        "factor": "Failure Reason",
        "value": failure.replace(
            "_",
            " "
        ),
        "impact": "DECISION INPUT"
    })

    # --------------------------------------------------------
    # Attempt safety
    # --------------------------------------------------------

    if attempts >= MAX_RECOVERY_ATTEMPTS:

        factors.append({
            "factor": "Safety Limit",
            "value": (
                f"{MAX_RECOVERY_ATTEMPTS} attempts reached"
            ),
            "impact": "ESCALATE"
        })

    elif attempts == MAX_RECOVERY_ATTEMPTS - 1:

        factors.append({
            "factor": "Attempt Safety",
            "value": (
                f"{attempts} attempts used"
            ),
            "impact": "CAUTION"
        })

    # --------------------------------------------------------
    # Recommended action
    # --------------------------------------------------------

    factors.append({
        "factor": "Recommended Action",
        "value": action,
        "impact": "RULE ENGINE DECISION"
    })

    # --------------------------------------------------------
    # Manual review factor
    # --------------------------------------------------------

    if action == "ESCALATE":

        factors.append({
            "factor": "Manual Review",
            "value": "Required",
            "impact": "ESCALATION"
        })

    return factors


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_transaction(transaction):

    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    score = calculate_recovery_score(
        transaction
    )

    # --------------------------------------------------------
    # Determine risk
    # --------------------------------------------------------

    risk = get_risk_level(
        score
    )

    # --------------------------------------------------------
    # Determine action
    # --------------------------------------------------------

    action = determine_action(
        transaction,
        score
    )

    # --------------------------------------------------------
    # Generate explanation
    # --------------------------------------------------------

    reason = generate_reason(
        transaction,
        score,
        action
    )

    # --------------------------------------------------------
    # Generate decision factors
    # --------------------------------------------------------

    decision_factors = generate_decision_factors(
        transaction,
        score,
        action
    )

    # --------------------------------------------------------
    # Return complete AI decision
    # --------------------------------------------------------

    return {

        "transaction_id":
            transaction.get(
                "transaction_id",
                ""
            ),

        "amount":
            transaction.get(
                "amount",
                0
            ),

        "status":
            transaction.get(
                "status",
                ""
            ),

        "failure_reason":
            transaction.get(
                "failure_reason",
                ""
            ),

        "recovery_score":
            score,

        "risk_level":
            risk,

        "recommended_action":
            action,

        "decision_reason":
            reason,

        "decision_factors":
            decision_factors
    }