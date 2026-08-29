# REVORA — AI Revenue Recovery

> **Find revenue that's slipping away and win it back.**

Revora is an AI-powered revenue recovery prototype that detects failed and abandoned payments, evaluates their recovery potential, recommends the right intervention, executes bounded recovery actions, and maintains a complete audit trail.

Built for the **Razorpay Buildathon — AI Revenue Recovery Track**.

---

## 🚨 Problem

Revenue can be lost through payment failures, checkout abandonment, insufficient funds, network errors, bank declines, expired cards, and other payment issues.

Simply detecting failed payments is not enough. Businesses need to know:

- Which payments are worth recovering?
- Why did they fail?
- What action should be taken?
- When should automation stop?
- When should a transaction be escalated?
- How much revenue was actually recovered?

---

## 💡 Solution

Revora closes the recovery loop:

Payment
   ↓
Failure Detection
   ↓
Recovery Score
   ↓
Risk Classification
   ↓
Decision Engine
   ↓
RETRY / REMIND / ESCALATE / STOP
   ↓
Bounded Recovery
   ↓
Measure Revenue
   ↓
Audit Trail

## ⚙️ Key Features
Recovery Scoring — Calculates a 0–100 recovery score using payment history, transaction amount, previous attempts, and customer type.
Risk Classification — Classifies transactions as HIGH, MEDIUM, or LOW risk.
Decision Engine — Recommends RETRY, REMIND, ESCALATE, or STOP.
Bounded Recovery — Limits automated recovery attempts to prevent uncontrolled retries.
Recovery Simulation — Simulates recovery and measures actual recovered revenue.
Explainable Decisions — Shows the reasoning and factors behind each recovery decision.
Compliance & Audit — Records decisions, actions, outcomes, and stopping rules.
Business Analytics — Tracks payment failures, recovery performance, and revenue impact.

## 🛡️ Safety & Escalation

Revora uses controlled recovery rules to keep automation bounded:

Maximum 3 automated recovery attempts
Successful payments are immediately stopped from further recovery
Unknown or unsafe failures can be ESCALATED for manual review
Every recovery action is recorded in the audit trail

Example:

3 attempts reached
       ↓
   ESCALATE
       ↓
 Manual Review

This prevents uncontrolled retries and provides a clear human-in-the-loop path.

## 📊 Dashboard

Revora provides four main views:

Overview

Provides an operational summary of:

Recoverable revenue
Recovered revenue
Recovery rate
Recovery attempts
AI recovery opportunities
Recent recovery decisions
Recovery

Displays transaction-level:

Recovery score
Risk level
Recovery probability
Recommended action
AI reasoning
Recovery outcome
Analytics

Provides business-level analysis of:

Transaction outcomes
Failure reasons
AI decision distribution
Recoverable revenue
Recovered revenue
Unrecovered opportunity
Compliance & Audit

Provides a traceable record of:

Recovery actions
Successful recoveries
Escalations
Stopped transactions
Execution status
Recovery amounts
Decision reasoning
Stopping rules
Audit timestamps

## 💰 Current Demo Results

Revora analyzes a synthetic batch of 10,000 transactions.

Metric	Result
Total Transactions	10,000
Failed Transactions	2,945
Recoverable Revenue	₹7.38 Cr
Recovered Revenue	₹0.64 L
Recovery Rate	0.09%

The dashboard provides both batch-level revenue metrics and transaction-level recovery traceability.

## 🧠 Example Recovery Decision
Transaction: TX10021
Amount: ₹4,493.39
Failure: INSUFFICIENT_FUNDS

Recovery Score: 74.2 / 100
Risk: HIGH
Probability: 90%
Action: RETRY

Result: RECOVERED
Recovered Amount: ₹4,493.39

Stopping Rule:
Recovery succeeded; further attempts stopped.

The complete decision, execution result, and stopping rule are recorded in the audit log.

## 🏗️ Tech Stack

Frontend

React
Vite
JavaScript
CSS

Backend

Python
Flask

Data Processing

Pandas
CSV

Architecture

React Frontend
      ↓
Flask REST API
      ↓
Decision Engine
      ↓
Recovery Simulator
      ↓
Audit & Analytics

## 📁 Project Structure
Revora/
├── backend/
│   ├── decision_engine.py
│   ├── recovery_simulator.py
│   ├── app.py
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Recovery.jsx
│   │   ├── Analytics.jsx
│   │   ├── Compliance.jsx
│   │   └── ...
│   └── ...
│
├── data/
│   └── transactions.csv
│
└── README.md

## ▶️ Run Locally
1. Start the Backend
cd backend
pip install flask flask-cors pandas
python app.py

Backend:

http://127.0.0.1:5000
2. Start the Frontend

Open another terminal:

cd frontend
npm install
npm run dev

Open the Vite URL shown in the terminal, usually:

http://localhost:5173
🔌 API Endpoints
GET /api/metrics
GET /api/results

/api/metrics provides batch-level recovery and revenue metrics.

/api/results provides transaction-level recovery decisions and outcomes.

## 🎯 End-to-End Workflow
Detect
  ↓
Diagnose
  ↓
Score
  ↓
Decide
  ↓
Recover
  ↓
Stop / Escalate
  ↓
Audit
  ↓
Measure

Revora demonstrates the complete journey from identifying revenue at risk to measuring recovered revenue while keeping automated actions bounded and traceable.

## 📌 Project Status

Prototype / Buildathon Demonstration

Revora currently uses synthetic transaction data and simulated recovery execution to demonstrate an end-to-end AI revenue recovery workflow.

It is designed as a proof-of-concept and is not connected to live payment processing.

REVORA — Detect. Decide. Recover. Measure. Audit.