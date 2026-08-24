from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os
from datetime import datetime

from decision_engine import analyze_transaction
from recovery_simulator import simulate_recovery
from metrics import calculate_metrics


app = Flask(__name__)
CORS(app)


# ==========================================
# FILE PATHS
# ==========================================

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

AUDIT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "recovery_audit.csv"
)


# ==========================================
# CSV HELPERS
# ==========================================

def load_csv(file_path):

    if not os.path.exists(file_path):
        return []

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
# AUDIT TRAIL
# ==========================================

def write_audit_log(
    transaction,
    decision,
    recovery
):

    audit_record = {
        "audit_timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "transaction_id":
            transaction.get(
                "transaction_id",
                ""
            ),

        "customer_id":
            transaction.get(
                "customer_id",
                ""
            ),

        "amount":
            transaction.get(
                "amount",
                0
            ),

        "failure_reason":
            transaction.get(
                "failure_reason",
                ""
            ),

        "recovery_score":
            decision.get(
                "recovery_score",
                ""
            ),

        "risk_level":
            decision.get(
                "risk_level",
                ""
            ),

        "recommended_action":
            decision.get(
                "recommended_action",
                ""
            ),

        "recovery_status":
            recovery.get(
                "recovery_status",
                ""
            ),

        "recovery_probability":
            recovery.get(
                "recovery_probability",
                ""
            ),

        "recovered_amount":
            recovery.get(
                "recovered_amount",
                0
            ),

        "attempts_before":
            recovery.get(
                "attempts_before",
                ""
            ),

        "attempts_after":
            recovery.get(
                "attempts_after",
                ""
            ),

        "action_executed":
            recovery.get(
                "action_executed",
                False
            ),

        "stopping_rule":
            recovery.get(
                "stopping_rule",
                ""
            ),

        "decision_reason":
            decision.get(
                "decision_reason",
                ""
            )
    }

    fieldnames = [
        "audit_timestamp",
        "transaction_id",
        "customer_id",
        "amount",
        "failure_reason",
        "recovery_score",
        "risk_level",
        "recommended_action",
        "recovery_status",
        "recovery_probability",
        "recovered_amount",
        "attempts_before",
        "attempts_after",
        "action_executed",
        "stopping_rule",
        "decision_reason"
    ]

    file_exists = os.path.exists(
        AUDIT_FILE
    )

    with open(
        AUDIT_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            audit_record
        )


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return jsonify({

        "application":
            "Revora",

        "message":
            "AI Revenue Recovery API is running",

        "status":
            "online"
    })


# ==========================================
# GET ALL TRANSACTIONS
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

        "count":
            len(transactions),

        "transactions":
            transactions
    })


# ==========================================
# GET RECOVERY RESULTS
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

    recovery_lookup = {
        result["transaction_id"]:
            result
        for result in recovery_results
    }

    results = []

    for transaction in transactions:

        transaction = convert_transaction(
            transaction
        )

        decision = analyze_transaction(
            transaction
        )

        transaction_id = transaction[
            "transaction_id"
        ]

        recovery = recovery_lookup.get(
            transaction_id,
            {}
        )

        result = {
            **decision,
            **recovery
        }

        # Preserve original transaction information

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

        "count":
            len(results),

        "results":
            results
    })


# ==========================================
# GET METRICS
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
            result.get(
                "recovered_amount",
                0
            )
        )

    metrics = calculate_metrics(
        results
    )

    return jsonify(metrics)


# ==========================================
# GET AUDIT TRAIL
# ==========================================

@app.route(
    "/api/audit",
    methods=["GET"]
)
def get_audit():

    audit_records = load_csv(
        AUDIT_FILE
    )

    return jsonify({

        "count":
            len(audit_records),

        "audit":
            audit_records
    })


# ==========================================
# ANALYZE TRANSACTION
# ==========================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze():

    transaction = request.get_json()

    if not transaction:

        return jsonify({

            "error":
                "Transaction data is required"

        }), 400

    try:

        transaction = convert_transaction(
            transaction
        )

        decision = analyze_transaction(
            transaction
        )

        return jsonify(
            decision
        )

    except Exception as error:

        return jsonify({

            "error":
                str(error)

        }), 500


# ==========================================
# EXECUTE RECOVERY
# ==========================================

@app.route(
    "/api/execute-recovery",
    methods=["POST"]
)
def execute_recovery():

    transaction = request.get_json()

    if not transaction:

        return jsonify({

            "error":
                "Transaction data is required"

        }), 400

    try:

        # ----------------------------------
        # Convert transaction
        # ----------------------------------

        transaction = convert_transaction(
            transaction
        )

        # ----------------------------------
        # AI DECISION
        # ----------------------------------

        decision = analyze_transaction(
            transaction
        )

        action = decision[
            "recommended_action"
        ]

        score = decision[
            "recovery_score"
        ]

        # ----------------------------------
        # EXECUTE BOUNDED RECOVERY
        # ----------------------------------

        recovery = simulate_recovery(
            transaction,
            action,
            score
        )

        # ----------------------------------
        # COMBINE RESULT
        # ----------------------------------

        result = {
            **decision,
            **recovery
        }

        # ----------------------------------
        # PERSIST RECOVERY RESULT
        # ----------------------------------

        recovery_results = load_csv(
            RESULTS_FILE
        )

        transaction_id = transaction[
            "transaction_id"
        ]

        existing_index = None

        for index, row in enumerate(
            recovery_results
        ):

            if row.get(
                "transaction_id"
            ) == transaction_id:

                existing_index = index
                break

        persistent_result = {
            **transaction,
            **decision,
            **recovery
        }

        if existing_index is not None:

            recovery_results[
                existing_index
            ] = persistent_result

        else:

            recovery_results.append(
                persistent_result
            )

        # ----------------------------------
        # WRITE RECOVERY RESULTS
        # ----------------------------------

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

        # ----------------------------------
        # WRITE ONE AUDIT EVENT
        # ----------------------------------

        write_audit_log(
            transaction,
            decision,
            recovery
        )

        # ----------------------------------
        # RETURN RESULT
        # ----------------------------------

        return jsonify(
            result
        )

    except Exception as error:

        print(
            "Recovery execution error:",
            error
        )

        return jsonify({

            "error":
                str(error)

        }), 500


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )