import csv
import os

from decision_engine import analyze_transaction
from recovery_simulator import simulate_recovery
from metrics import calculate_metrics


# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(BASE_DIR, "data", "transactions.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "recovery_results.csv")


def load_transactions():
    transactions = []

    with open(INPUT_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["amount"] = float(row["amount"])
            row["attempt_count"] = int(row["attempt_count"])
            row["previous_success_rate"] = float(row["previous_success_rate"])
            row["days_since_last_payment"] = int(row["days_since_last_payment"])

            transactions.append(row)

    return transactions


def process_transactions(transactions):
    results = []

    for transaction in transactions:

        # Step 1: Revora analyzes the transaction
        decision = analyze_transaction(transaction)

        # Step 2: Simulate the recovery
        recovery = simulate_recovery(
            transaction,
            decision["recommended_action"],
            decision["recovery_score"]
        )

        # Step 3: Combine decision + recovery result
        result = {
            **decision,
            **recovery
        }

        results.append(result)

    return results


def save_results(results):

    fieldnames = [
        "transaction_id",
        "amount",
        "status",
        "failure_reason",
        "recovery_score",
        "risk_level",
        "recommended_action",
        "decision_reason",
        "recovery_probability",
        "recovery_status",
        "recovered_amount"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)


def print_summary(metrics):

    print("\n===================================")
    print("        REVORA ANALYSIS")
    print("===================================")

    print(f"Total Transactions : {metrics['total_transactions']}")
    print(f"Failed Transactions: {metrics['failed_transactions']}")

    print(
        f"Recoverable Revenue: ₹{metrics['recoverable_revenue']:,.2f}"
    )

    print(
        f"Recovered Revenue  : ₹{metrics['recovered_revenue']:,.2f}"
    )

    print(
        f"Recovery Rate      : {metrics['recovery_rate']:.2f}%"
    )

    print(
        f"Recovery Attempts  : {metrics['recovery_attempts']}"
    )

    print(
        f"Stopped Transactions: {metrics['stopped_transactions']}"
    )

    print("===================================")


def main():

    print("Loading transactions...")

    transactions = load_transactions()

    print(f"Loaded {len(transactions)} transactions.")

    print("Running Revora decision engine...")

    results = process_transactions(transactions)

    print("Saving recovery results...")

    save_results(results)

    print("Calculating metrics...")

    metrics = calculate_metrics(results)

    print_summary(metrics)

    print("\nAnalysis completed successfully!")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()