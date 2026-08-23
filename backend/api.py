from flask import Flask, jsonify, request
import csv
import os

from decision_engine import analyze_transaction
from recovery_simulator import simulate_recovery
from metrics import calculate_metrics


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(BASE_DIR, "data", "transactions.csv")
RESULTS_FILE = os.path.join(BASE_DIR, "data", "recovery_results.csv")


def load_csv(file_path):
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def convert_transaction(transaction):
    transaction["amount"] = float(transaction["amount"])
    transaction["attempt_count"] = int(transaction["attempt_count"])
    transaction["previous_success_rate"] = float(
        transaction["previous_success_rate"]
    )
    transaction["days_since_last_payment"] = int(
        transaction["days_since_last_payment"]
    )

    return transaction


# Home
@app.route("/")
def home():
    return jsonify({
        "application": "Revora",
        "message": "AI Revenue Recovery API is running",
        "status": "online"
    })


# Get all transactions
@app.route("/api/transactions", methods=["GET"])
def get_transactions():

    transactions = load_csv(INPUT_FILE)

    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })


# Get recovery results
@app.route("/api/results", methods=["GET"])
def get_results():

    results = load_csv(RESULTS_FILE)

    return jsonify({
        "count": len(results),
        "results": results
    })


# Get metrics
@app.route("/api/metrics", methods=["GET"])
def get_metrics():

    results = load_csv(RESULTS_FILE)

    for result in results:
        result["amount"] = float(result["amount"])
        result["recovered_amount"] = float(result["recovered_amount"])

    metrics = calculate_metrics(results)

    return jsonify(metrics)


# Analyze a single transaction
@app.route("/api/analyze", methods=["POST"])
def analyze():

    transaction = request.get_json()

    if not transaction:
        return jsonify({
            "error": "Transaction data is required"
        }), 400

    transaction = convert_transaction(transaction)

    decision = analyze_transaction(transaction)

    recovery = simulate_recovery(
        transaction,
        decision["recommended_action"],
        decision["recovery_score"]
    )

    result = {
        **decision,
        **recovery
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )