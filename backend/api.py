from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os

from decision_engine import analyze_transaction
from recovery_simulator import simulate_recovery
from metrics import calculate_metrics


app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "transactions.csv"
)

RESULTS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "recovery_results.csv"
)


def load_csv(file_path):
    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        return list(
            csv.DictReader(file)
        )


def convert_transaction(transaction):
    transaction = transaction.copy()

    transaction["amount"] = float(
        transaction["amount"]
    )

    transaction["attempt_count"] = int(
        transaction["attempt_count"]
    )

    transaction["previous_success_rate"] = float(
        transaction["previous_success_rate"]
    )

    transaction["days_since_last_payment"] = int(
        transaction["days_since_last_payment"]
    )

    return transaction


# ==========================================
# Home
# ==========================================

@app.route("/")
def home():

    return jsonify({
        "application": "Revora",
        "message": "AI Revenue Recovery API is running",
        "status": "online"
    })


# ==========================================
# Get all transactions
# ==========================================

@app.route(
    "/api/transactions",
    methods=["GET"]
)
def get_transactions():

    transactions = load_csv(
        INPUT_FILE
    )

    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })


# ==========================================
# Get recovery results
# ==========================================

@app.route(
    "/api/results",
    methods=["GET"]
)
def get_results():

    transactions = load_csv(
        INPUT_FILE
    )

    recovery_results = load_csv(
        RESULTS_FILE
    )

    # Create lookup for existing
    # recovery simulation results
    recovery_lookup = {
        result["transaction_id"]: result
        for result in recovery_results
    }

    results = []

    for transaction in transactions:

        transaction = convert_transaction(
            transaction
        )

        # Generate the latest AI decision
        decision = analyze_transaction(
            transaction
        )

        transaction_id = transaction[
            "transaction_id"
        ]

        # Get previously simulated recovery
        # information if available
        recovery = recovery_lookup.get(
            transaction_id,
            {}
        )

        result = {
            **decision,
            **recovery
        }

        # Make sure original transaction
        # information is preserved
        result["transaction_id"] = (
            transaction["transaction_id"]
        )

        result["customer_id"] = (
            transaction["customer_id"]
        )

        result["amount"] = (
            transaction["amount"]
        )

        result["status"] = (
            transaction["status"]
        )

        result["failure_reason"] = (
            transaction["failure_reason"]
        )

        result["attempt_count"] = (
            transaction["attempt_count"]
        )

        result["previous_success_rate"] = (
            transaction[
                "previous_success_rate"
            ]
        )

        result["days_since_last_payment"] = (
            transaction[
                "days_since_last_payment"
            ]
        )

        result["payment_method"] = (
            transaction["payment_method"]
        )

        result["customer_type"] = (
            transaction["customer_type"]
        )

        result["timestamp"] = (
            transaction["timestamp"]
        )

        results.append(result)

    return jsonify({
        "count": len(results),
        "results": results
    })


# ==========================================
# Get metrics
# ==========================================

@app.route(
    "/api/metrics",
    methods=["GET"]
)
def get_metrics():

    results = load_csv(
        RESULTS_FILE
    )

    for result in results:

        result["amount"] = float(
            result["amount"]
        )

        result["recovered_amount"] = float(
            result["recovered_amount"]
        )

    metrics = calculate_metrics(
        results
    )

    return jsonify(metrics)


# ==========================================
# Analyze a single transaction
# ==========================================

@app.route("/api/analyze", methods=["POST"])
def analyze():
    # Your existing analyze logic is here
    # Keep all of this unchanged
    pass


# Execute a recovery action
# ==========================================
# Execute a recovery action
# ==========================================

@app.route("/api/execute-recovery", methods=["POST"])
def execute_recovery():

    transaction = request.get_json()

    if not transaction:
        return jsonify({
            "error": "Transaction data is required"
        }), 400

    try:

        # ------------------------------------------
        # Convert transaction data
        # ------------------------------------------

        transaction = convert_transaction(
            transaction
        )

        # ------------------------------------------
        # Run AI decision engine
        # ------------------------------------------

        decision = analyze_transaction(
            transaction
        )

        action = decision["recommended_action"]
        score = decision["recovery_score"]

        # ------------------------------------------
        # Execute bounded recovery workflow
        # ------------------------------------------

        recovery = simulate_recovery(
            transaction,
            action,
            score
        )

        # ------------------------------------------
        # Combine AI decision + recovery result
        # ------------------------------------------

        result = {
            **decision,
            **recovery
        }

        # ------------------------------------------
        # Persist recovery result
        # ------------------------------------------

        recovery_results = load_csv(
            RESULTS_FILE
        )

        transaction_id = transaction[
            "transaction_id"
        ]

        # Check whether this transaction
        # already exists in recovery results
        existing_index = None

        for index, row in enumerate(
            recovery_results
        ):
            if row.get(
                "transaction_id"
            ) == transaction_id:
                existing_index = index
                break

        # ------------------------------------------
        # Build persistent recovery record
        # ------------------------------------------

        persistent_result = {
            **transaction,
            **decision,
            **recovery
        }

        # ------------------------------------------
        # Update existing record
        # or add a new record
        # ------------------------------------------

        if existing_index is not None:

            recovery_results[
                existing_index
            ] = persistent_result

        else:

            recovery_results.append(
                persistent_result
            )

        # ------------------------------------------
        # Write updated results to CSV
        # ------------------------------------------

        if recovery_results:

            fieldnames = list(
                recovery_results[0].keys()
            )

            with open(
                RESULTS_FILE,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames,
                    extrasaction="ignore"
                )

                writer.writeheader()

                writer.writerows(
                    recovery_results
                )

        # ------------------------------------------
        # Return result to frontend
        # ------------------------------------------

        return jsonify(result)

    except Exception as error:

        print(
            "Recovery execution error:",
            error
        )

        return jsonify({
            "error": str(error)
        }), 500

# ==========================================
# Run server
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )