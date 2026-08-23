def calculate_metrics(results):

    total_transactions = len(results)

    # --------------------------------
    # Failed / abandoned transactions
    # --------------------------------

    failed_transactions = sum(
        1
        for r in results
        if r["status"] in ["FAILED", "ABANDONED"]
    )

    # --------------------------------
    # Revenue at risk
    # --------------------------------

    recoverable_revenue = sum(
        float(r.get("amount", 0))
        for r in results
        if r["status"] in ["FAILED", "ABANDONED"]
    )

    # --------------------------------
    # Successfully recovered revenue
    # --------------------------------

    recovered_revenue = sum(
        float(r.get("recovered_amount", 0))
        for r in results
        if r.get("recovery_status") == "RECOVERED"
    )

    # --------------------------------
    # Revenue still at risk
    # --------------------------------

    remaining_revenue_at_risk = max(
        recoverable_revenue - recovered_revenue,
        0
    )

    # --------------------------------
    # Recovery rate
    # --------------------------------

    recovery_rate = 0

    if recoverable_revenue > 0:
        recovery_rate = (
            recovered_revenue /
            recoverable_revenue
        ) * 100

    # --------------------------------
    # Recovery opportunities
    # --------------------------------

    recovery_opportunities = sum(
        1
        for r in results
        if r.get("recommended_action") in [
            "RETRY",
            "REMIND",
            "ESCALATE"
        ]
    )

    # --------------------------------
    # Recovery attempts
    # --------------------------------

    recovery_attempts = sum(
        1
        for r in results
        if r.get("recovery_status") in [
            "RECOVERED",
            "FAILED"
        ]
    )

    # --------------------------------
    # Successful recoveries
    # --------------------------------

    successful_recoveries = sum(
        1
        for r in results
        if r.get("recovery_status") == "RECOVERED"
    )

    # --------------------------------
    # Stopped transactions
    # --------------------------------

    stopped_transactions = sum(
        1
        for r in results
        if r.get("recommended_action") == "STOP"
    )

    # --------------------------------
    # Escalated transactions
    # --------------------------------

    escalated_transactions = sum(
        1
        for r in results
        if r.get("recovery_status") == "ESCALATED"
    )

    return {

        "total_transactions":
            total_transactions,

        "failed_transactions":
            failed_transactions,

        "recovery_opportunities":
            recovery_opportunities,

        "recoverable_revenue":
            round(recoverable_revenue, 2),

        "recovered_revenue":
            round(recovered_revenue, 2),

        "remaining_revenue_at_risk":
            round(remaining_revenue_at_risk, 2),

        "recovery_rate":
            round(recovery_rate, 2),

        "recovery_attempts":
            recovery_attempts,

        "successful_recoveries":
            successful_recoveries,

        "stopped_transactions":
            stopped_transactions,

        "escalated_transactions":
            escalated_transactions
    }