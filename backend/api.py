# ============================================================
# REVORA - FLASK API
# ============================================================

from flask import Flask, jsonify, request
from flask_cors import CORS

import csv
import os
from datetime import datetime

from decision_engine import analyze_transaction
from recovery_simulator import simulate_recovery
from metrics import calculate_metrics


# ============================================================
# APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

INPUT_FILE = os.path.join(
    DATA_DIR,
    "transactions.csv"
)

RESULTS_FILE = os.path.join(
    DATA_DIR,
    "recovery_results.csv"
)

AUDIT_FILE = os.path.join(
    DATA_DIR,
    "recovery_audit.csv"
)


os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# ============================================================
# CSV HELPERS
# ============================================================

def load_csv(file_path):

    if not os.path.exists(file_path):
        return []

    try:

        with open(
            file_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            return list(
                csv.DictReader(file)
            )

    except Exception as error:

        print(
            f"CSV loading error ({file_path}):",
            error
        )

        return []


def write_csv(file_path, records):

    if not records:
        return

    # Collect ALL fields from ALL records.
    # This prevents fields from being lost when
    # different records contain different keys.

    fieldnames = []

    for record in records:

        for key in record.keys():

            if key not in fieldnames:
                fieldnames.append(key)

    with open(
        file_path,
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
            records
        )


# ============================================================
# TYPE CONVERSION
# ============================================================

def safe_float(value, default=0):

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):
        return default


def safe_int(value, default=0):

    try:
        return int(float(value))

    except (
        TypeError,
        ValueError
    ):
        return default


def convert_transaction(transaction):

    transaction = transaction.copy()

    transaction["amount"] = safe_float(
        transaction.get(
            "amount",
            0
        )
    )

    transaction["attempt_count"] = safe_int(
        transaction.get(
            "attempt_count",
            0
        )
    )

    transaction["previous_success_rate"] = safe_float(
        transaction.get(
            "previous_success_rate",
            0
        )
    )

    transaction["days_since_last_payment"] = safe_int(
        transaction.get(
            "days_since_last_payment",
            0
        )
    )

    return transaction


# ============================================================
# BUILD CURRENT AI RESULTS
# ============================================================

def build_results():

    transactions = load_csv(
        INPUT_FILE
    )

    recovery_results = load_csv(
        RESULTS_FILE
    )

    recovery_lookup = {
        result.get("transaction_id"): result
        for result in recovery_results
        if result.get("transaction_id")
    }

    results = []

    for raw_transaction in transactions:

        transaction = convert_transaction(
            raw_transaction
        )

        decision = analyze_transaction(
            transaction
        )

        transaction_id = transaction.get(
            "transaction_id",
            ""
        )

        # Existing execution history, if any
        recovery = recovery_lookup.get(
            transaction_id,
            {}
        )

        # ----------------------------------------------------
        # Merge in controlled order
        # ----------------------------------------------------

        result = {
            **transaction,
            **decision,
            **recovery
        }

        # ----------------------------------------------------
        # Always preserve CURRENT transaction information
        # ----------------------------------------------------

        result["transaction_id"] = transaction.get(
            "transaction_id",
            ""
        )

        result["customer_id"] = transaction.get(
            "customer_id",
            ""
        )

        result["amount"] = transaction.get(
            "amount",
            0
        )

        result["status"] = transaction.get(
            "status",
            ""
        )

        result["failure_reason"] = transaction.get(
            "failure_reason",
            ""
        )

        result["attempt_count"] = transaction.get(
            "attempt_count",
            0
        )

        result["previous_success_rate"] = transaction.get(
            "previous_success_rate",
            0
        )

        result["days_since_last_payment"] = transaction.get(
            "days_since_last_payment",
            0
        )

        result["payment_method"] = transaction.get(
            "payment_method",
            ""
        )

        result["customer_type"] = transaction.get(
            "customer_type",
            ""
        )

        result["timestamp"] = transaction.get(
            "timestamp",
            ""
        )

        results.append(
            result
        )

    return results


# ============================================================
# AUDIT WRITER
# ============================================================

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

    # --------------------------------------------------------
    # Prevent exact duplicate event
    # --------------------------------------------------------

    existing_records = load_csv(
        AUDIT_FILE
    )

    for existing in existing_records:

        same_event = (

            existing.get(
                "transaction_id",
                ""
            )
            ==
            str(
                audit_record[
                    "transaction_id"
                ]
            )

            and

            existing.get(
                "attempts_before",
                ""
            )
            ==
            str(
                audit_record[
                    "attempts_before"
                ]
            )

            and

            existing.get(
                "attempts_after",
                ""
            )
            ==
            str(
                audit_record[
                    "attempts_after"
                ]
            )

            and

            existing.get(
                "recommended_action",
                ""
            )
            ==
            str(
                audit_record[
                    "recommended_action"
                ]
            )

            and

            existing.get(
                "recovery_status",
                ""
            )
            ==
            str(
                audit_record[
                    "recovery_status"
                ]
            )
        )

        if same_event:

            print(
                "Duplicate audit event skipped:",
                audit_record["transaction_id"]
            )

            return

    existing_records.append(
        audit_record
    )

    write_csv(
        AUDIT_FILE,
        existing_records
    )


# ============================================================
# HOME
# ============================================================

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


# ============================================================
# GET ALL TRANSACTIONS
# ============================================================

@app.route(
    "/api/transactions",
    methods=["GET"]
)
def get_transactions():

    transactions = load_csv(
        INPUT_FILE
    )

    converted = [
        convert_transaction(transaction)
        for transaction in transactions
    ]

    return jsonify({

        "count":
            len(converted),

        "transactions":
            converted
    })


# ============================================================
# GET RECOVERY RESULTS
# ============================================================

@app.route(
    "/api/results",
    methods=["GET"]
)
def get_results():

    results = build_results()

    return jsonify({

        "count":
            len(results),

        "results":
            results
    })


# ============================================================
# GET METRICS
# ============================================================

@app.route(
    "/api/metrics",
    methods=["GET"]
)
def get_metrics():

    try:

        # ----------------------------------------------------
        # Use current transaction + decision data
        # ----------------------------------------------------

        results = build_results()

        cleaned_results = []

        for result in results:

            result = result.copy()

            result["amount"] = safe_float(
                result.get(
                    "amount",
                    0
                )
            )

            result["recovered_amount"] = safe_float(
                result.get(
                    "recovered_amount",
                    0
                )
            )

            result["recovery_probability"] = safe_float(
                result.get(
                    "recovery_probability",
                    0
                )
            )

            result["recovery_score"] = safe_float(
                result.get(
                    "recovery_score",
                    0
                )
            )

            result["attempts_before"] = safe_int(
                result.get(
                    "attempts_before",
                    0
                )
            )

            result["attempts_after"] = safe_int(
                result.get(
                    "attempts_after",
                    0
                )
            )

            cleaned_results.append(
                result
            )

        metrics = calculate_metrics(
            cleaned_results
        )

        return jsonify(
            metrics
        )

    except Exception as error:

        print(
            "Metrics error:",
            error
        )

        return jsonify({

            "error":
                "Failed to calculate metrics",

            "details":
                str(error)

        }), 500


# ============================================================
# GET AUDIT LOG
# ============================================================

@app.route(
    "/api/audit",
    methods=["GET"]
)
def get_audit():

    try:

        audit_records = load_csv(
            AUDIT_FILE
        )

        for record in audit_records:

            # Amount

            if record.get("amount"):

                record["amount"] = safe_float(
                    record["amount"]
                )

            # Recovery probability

            if record.get(
                "recovery_probability"
            ):

                record[
                    "recovery_probability"
                ] = safe_float(
                    record[
                        "recovery_probability"
                    ]
                )

            # Recovery score

            if record.get(
                "recovery_score"
            ):

                record[
                    "recovery_score"
                ] = safe_float(
                    record[
                        "recovery_score"
                    ]
                )

            # Attempts before

            if record.get(
                "attempts_before"
            ):

                record[
                    "attempts_before"
                ] = safe_int(
                    record[
                        "attempts_before"
                    ]
                )

            # Attempts after

            if record.get(
                "attempts_after"
            ):

                record[
                    "attempts_after"
                ] = safe_int(
                    record[
                        "attempts_after"
                    ]
                )

            # Boolean

            if record.get(
                "action_executed"
            ):

                record[
                    "action_executed"
                ] = (
                    str(
                        record[
                            "action_executed"
                        ]
                    ).lower()
                    == "true"
                )

        return jsonify({

            "count":
                len(audit_records),

            "audit":
                audit_records
        })

    except Exception as error:

        print(
            "Audit retrieval error:",
            error
        )

        return jsonify({

            "error":
                "Failed to load audit records",

            "details":
                str(error)

        }), 500


# ============================================================
# ANALYZE SINGLE TRANSACTION
# ============================================================

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

        print(
            "Analysis error:",
            error
        )

        return jsonify({

            "error":
                str(error)

        }), 500


# ============================================================
# EXECUTE RECOVERY
# ============================================================

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

        # ----------------------------------------------------
        # Convert transaction
        # ----------------------------------------------------

        transaction = convert_transaction(
            transaction
        )

        # ----------------------------------------------------
        # AI DECISION
        # ----------------------------------------------------

        decision = analyze_transaction(
            transaction
        )

        action = decision[
            "recommended_action"
        ]

        score = decision[
            "recovery_score"
        ]

        # ----------------------------------------------------
        # EXECUTE BOUNDED RECOVERY
        # ----------------------------------------------------

        recovery = simulate_recovery(
            transaction,
            action,
            score
        )

        # ----------------------------------------------------
        # COMBINE RESULT
        # ----------------------------------------------------

        result = {
            **transaction,
            **decision,
            **recovery
        }

        # ----------------------------------------------------
        # PERSIST RECOVERY RESULT
        # ----------------------------------------------------

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

        write_csv(
            RESULTS_FILE,
            recovery_results
        )

        # ----------------------------------------------------
        # WRITE AUDIT EVENT
        # ----------------------------------------------------

        write_audit_log(
            transaction,
            decision,
            recovery
        )

        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

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


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )