def calculate_metrics(results):

    total_transactions = len(results)

    failed_transactions = sum(
        1 for r in results
        if r["status"] in ["FAILED", "ABANDONED"]
    )

    recoverable_revenue = sum(
        r["amount"]
        for r in results
        if r["status"] in ["FAILED", "ABANDONED"]
    )

    recovered_revenue = sum(
        r["recovered_amount"]
        for r in results
    )

    recovery_rate = 0

    if recoverable_revenue > 0:
        recovery_rate = (
            recovered_revenue / recoverable_revenue
        ) * 100

    recovery_attempts = sum(
        1 for r in results
        if r["recommended_action"] in [
            "RETRY",
            "REMIND",
            "ESCALATE"
        ]
    )

    stopped_transactions = sum(
        1 for r in results
        if r["recommended_action"] == "STOP"
    )

    return {
        "total_transactions": total_transactions,
        "failed_transactions": failed_transactions,
        "recoverable_revenue": round(recoverable_revenue, 2),
        "recovered_revenue": round(recovered_revenue, 2),
        "recovery_rate": round(recovery_rate, 2),
        "recovery_attempts": recovery_attempts,
        "stopped_transactions": stopped_transactions
    }