import csv
import random
from datetime import datetime, timedelta

NUM_TRANSACTIONS = 10000

statuses = ["SUCCESS", "FAILED", "ABANDONED"]
status_weights = [70, 20, 10]

failure_reasons = [
    "INSUFFICIENT_FUNDS",
    "BANK_DECLINE",
    "NETWORK_ERROR",
    "CARD_EXPIRED",
    "LIMIT_EXCEEDED",
    "UNKNOWN"
]

payment_methods = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET"]
customer_types = ["NEW", "RETURNING"]

rows = []

start_date = datetime(2026, 1, 1)

for i in range(NUM_TRANSACTIONS):

    transaction_id = f"TX{10001 + i}"
    customer_id = f"CUST{random.randint(100, 999)}"

    amount = round(random.uniform(100, 50000), 2)

    status = random.choices(
        statuses,
        weights=status_weights,
        k=1
    )[0]

    if status == "FAILED":
        failure_reason = random.choice(failure_reasons)
        recovery_status = "PENDING"
    elif status == "ABANDONED":
        failure_reason = "UNKNOWN"
        recovery_status = "PENDING"
    else:
        failure_reason = "NONE"
        recovery_status = "NOT_REQUIRED"

    attempt_count = random.randint(1, 3)

    previous_success_rate = round(random.uniform(0.40, 1.00), 2)

    days_since_last_payment = random.randint(0, 60)

    payment_method = random.choice(payment_methods)

    customer_type = random.choice(customer_types)

    timestamp = start_date + timedelta(
        days=random.randint(0, 231),
        minutes=random.randint(0, 1439)
    )

    rows.append([
        transaction_id,
        customer_id,
        amount,
        status,
        failure_reason,
        attempt_count,
        previous_success_rate,
        days_since_last_payment,
        payment_method,
        customer_type,
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        recovery_status
    ])


output_file = "transactions.csv"

with open(output_file, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "transaction_id",
        "customer_id",
        "amount",
        "status",
        "failure_reason",
        "attempt_count",
        "previous_success_rate",
        "days_since_last_payment",
        "payment_method",
        "customer_type",
        "timestamp",
        "recovery_status"
    ])

    writer.writerows(rows)

print(f"Successfully generated {NUM_TRANSACTIONS} transactions.")
print(f"File created: {output_file}")