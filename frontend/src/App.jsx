import { useEffect, useState } from "react";
import "./App.css";
import Transactions from "./Transactions";
import Recovery from "./Recovery";
import Analytics from "./Analytics";

function App() {
  const [metrics, setMetrics] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activePage, setActivePage] = useState("overview");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const metricsResponse = await fetch(
          "http://127.0.0.1:5000/api/metrics"
        );

        const resultsResponse = await fetch(
          "http://127.0.0.1:5000/api/results"
        );

        if (!metricsResponse.ok || !resultsResponse.ok) {
          throw new Error("Failed to fetch Revora API data");
        }

        const metricsData = await metricsResponse.json();
        const resultsData = await resultsResponse.json();

        setMetrics(metricsData);
        setResults(resultsData.results || []);
      } catch (error) {
        console.error("Failed to load Revora data:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  /* Loading state */
  if (loading) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>Loading revenue intelligence...</p>
      </div>
    );
  }

  /* Backend/API error state */
  if (!metrics) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>Unable to load dashboard data.</p>

        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: "15px",
            padding: "10px 18px",
            border: "none",
            borderRadius: "8px",
            background: "#111827",
            color: "white",
            cursor: "pointer",
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  /* Top 3 AI recovery opportunities */
  const topRecoveryOpportunities = [...results]
    .sort(
      (a, b) =>
        Number(b.recovery_probability || 0) -
        Number(a.recovery_probability || 0)
    )
    .slice(0, 3);

  /* Average recovery probability */
  const recoveryDecisions = results.filter(
    (item) => Number(item.recovery_probability || 0) > 0
  );

  const averageRecoveryProbability =
    recoveryDecisions.length > 0
      ? (
          (recoveryDecisions.reduce(
            (sum, item) =>
              sum + Number(item.recovery_probability || 0) * 100,
            0
          ) /
            recoveryDecisions.length)
        ).toFixed(1)
      : "0.0";

  return (
    <div className="app">

      {/* ============================= */}
      {/* Sidebar                       */}
      {/* ============================= */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-mark">
            R
          </div>

          <div>
            <h2>REVORA</h2>
            <span>Revenue Intelligence</span>
          </div>

        </div>


        {/* Navigation */}

        <nav>

          <a
            className={`nav-item ${
              activePage === "overview" ? "active" : ""
            }`}
            onClick={() => setActivePage("overview")}
          >
            Overview
          </a>


          <a
            className={`nav-item ${
              activePage === "transactions" ? "active" : ""
            }`}
            onClick={() => setActivePage("transactions")}
          >
            Transactions
          </a>


          <a
            className={`nav-item ${
              activePage === "recovery" ? "active" : ""
            }`}
            onClick={() => setActivePage("recovery")}
          >
            Recovery
          </a>


          <a
            className={`nav-item ${
              activePage === "analytics" ? "active" : ""
            }`}
            onClick={() => setActivePage("analytics")}
          >
            Analytics
          </a>

        </nav>


        <div className="sidebar-bottom">

          <div className="system-status">
            <span className="status-dot"></span>
            System Operational
          </div>

        </div>

      </aside>


      {/* ============================= */}
      {/* Main Content                  */}
      {/* ============================= */}

      <main className="main-content">

        {/* TRANSACTIONS PAGE */}
{activePage === "transactions" ? (
  <Transactions />
) : activePage === "recovery" ? (
  <Recovery />
) : activePage === "analytics" ? (
    <Analytics />
      ) : (

          /* ============================= */
          /* OVERVIEW PAGE                 */
          /* ============================= */

          <>

            {/* Header */}

            <header className="topbar">

              <div>

                <p className="eyebrow">
                  AI REVENUE RECOVERY
                </p>

                <h1>
                  Recovery Overview
                </h1>

                <p className="subtitle">
                  Monitor payment recovery and revenue performance.
                </p>

              </div>


              <div className="live-badge">
                <span></span>
                LIVE DATA
              </div>

            </header>


            {/* ============================= */}
            {/* KPI METRICS                   */}
            {/* ============================= */}

            <section className="metrics-grid">


              {/* Recoverable Revenue */}

              <div className="metric-card">

                <div className="metric-top">

                  <p>
                    Recoverable Revenue
                  </p>

                  <div className="metric-icon">
                    ₹
                  </div>

                </div>

                <h2>
                  ₹
                  {(
                    metrics.recoverable_revenue / 100000
                  ).toFixed(2)}
                  L
                </h2>

                <span>
                  Potential revenue identified
                </span>

              </div>


              {/* Recovered Revenue */}

              <div className="metric-card featured">

                <div className="metric-top">

                  <p>
                    Recovered Revenue
                  </p>

                  <div className="metric-icon">
                    ✓
                  </div>

                </div>

                <h2>
                  ₹
                  {(
                    metrics.recovered_revenue / 100000
                  ).toFixed(2)}
                  L
                </h2>

                <span>
                  Successfully recovered
                </span>

              </div>


              {/* Recovery Rate */}

              <div className="metric-card">

                <div className="metric-top">

                  <p>
                    Recovery Rate
                  </p>

                  <div className="metric-icon">
                    ↗
                  </div>

                </div>

                <h2>
                  {metrics.recovery_rate}%
                </h2>

                <span>
                  Overall recovery performance
                </span>

              </div>


              {/* Recovery Attempts */}

              <div className="metric-card">

                <div className="metric-top">

                  <p>
                    Recovery Attempts
                  </p>

                  <div className="metric-icon">
                    ⚡
                  </div>

                </div>

                <h2>
                  {metrics.recovery_attempts.toLocaleString()}
                </h2>

                <span>
                  AI-generated recovery actions
                </span>

              </div>


              {/* Average Recovery Probability */}

              <div className="metric-card ai-card">

                <div className="metric-top">

                  <p>
                    Avg. Recovery Probability
                  </p>

                  <div className="metric-icon">
                    AI
                  </div>

                </div>

                <h2>
                  {averageRecoveryProbability}%
                </h2>

                <span>
                  AI confidence across decisions
                </span>

              </div>

            </section>


            {/* ============================= */}
            {/* AI RECOVERY INTELLIGENCE      */}
            {/* ============================= */}

            <section className="panel ai-intelligence-panel">

              <div className="panel-header ai-header">

                <div>

                  <div className="ai-title-row">

                    <div className="ai-badge">
                      AI
                    </div>

                    <div>

                      <h3>
                        AI Recovery Intelligence
                      </h3>

                      <p>
                        High-confidence recovery opportunities identified by Revora
                      </p>

                    </div>

                  </div>

                </div>


                <div className="ai-status">
                  ● AI ACTIVE
                </div>

              </div>


              <div className="opportunity-grid">

                {topRecoveryOpportunities.map(
                  (transaction) => {

                    const probability =
                      Number(
                        transaction.recovery_probability || 0
                      ) * 100;

                    const score =
                      Number(
                        transaction.recovery_score || 0
                      );


                    return (

                      <div
                        className="opportunity-card"
                        key={transaction.transaction_id}
                      >

                        {/* Transaction */}

                        <div className="opportunity-top">

                          <div>

                            <span className="transaction-label">
                              TRANSACTION
                            </span>

                            <h4>
                              {transaction.transaction_id}
                            </h4>

                          </div>

                          <strong className="opportunity-amount">
                            ₹
                            {Number(
                              transaction.amount || 0
                            ).toLocaleString("en-IN")}
                          </strong>

                        </div>


                        {/* Failure */}

                        <div className="failure-box">

                          <span>
                            FAILURE REASON
                          </span>

                          <strong>
                            {transaction.failure_reason
                              ? transaction.failure_reason.replaceAll(
                                  "_",
                                  " "
                                )
                              : "UNKNOWN"}
                          </strong>

                        </div>


                        {/* AI Metrics */}

                        <div className="ai-metrics">

                          <div>

                            <span>
                              Recovery Score
                            </span>

                            <strong>
                              {score.toFixed(1)}
                            </strong>

                          </div>


                          <div>

                            <span>
                              Probability
                            </span>

                            <strong>
                              {probability.toFixed(0)}%
                            </strong>

                          </div>


                          <div>

                            <span>
                              Risk
                            </span>

                            <span
                              className={`risk ${
                                (
                                  transaction.risk_level ||
                                  "low"
                                ).toLowerCase()
                              }`}
                            >
                              {transaction.risk_level || "LOW"}
                            </span>

                          </div>

                        </div>


                        {/* Probability */}

                        <div className="probability-section">

                          <div className="probability-label">

                            <span>
                              Recovery probability
                            </span>

                            <strong>
                              {probability.toFixed(0)}%
                            </strong>

                          </div>


                          <div className="probability-track">

                            <div
                              className="probability-fill"
                              style={{
                                width: `${Math.min(
                                  probability,
                                  100
                                )}%`,
                              }}
                            ></div>

                          </div>

                        </div>


                        {/* Recommendation */}

                        <div className="recommendation">

                          <span>
                            RECOMMENDED ACTION
                          </span>

                          <strong>
                            {transaction.recommended_action ||
                              "STOP"}
                          </strong>

                        </div>


                        {/* AI Reasoning */}

                        <div className="ai-reason">

                          <span>
                            AI REASONING
                          </span>

                          <p>
                            {transaction.decision_reason ||
                              transaction.decision_rationale ||
                              "Revora recommends this action based on transaction recovery signals."}
                          </p>

                        </div>

                      </div>

                    );

                  }
                )}

              </div>

            </section>


            {/* ============================= */}
            {/* PERFORMANCE                   */}
            {/* ============================= */}

            <section className="content-grid">


              <div className="panel performance-panel">

                <div className="panel-header">

                  <div>

                    <h3>
                      Recovery Performance
                    </h3>

                    <p>
                      Revenue recovery from failed payments
                    </p>

                  </div>

                </div>


                <div className="recovery-display">

                  <div className="recovery-number">
                    {metrics.recovery_rate}%
                  </div>

                  <p>
                    Recovery Rate
                  </p>


                  <div className="progress-track">

                    <div
                      className="progress-fill"
                      style={{
                        width: `${Math.min(
                          metrics.recovery_rate,
                          100
                        )}%`,
                      }}
                    ></div>

                  </div>


                  <div className="recovery-details">

                    <div>

                      <span>
                        Recoverable
                      </span>

                      <strong>
                        ₹
                        {(
                          metrics.recoverable_revenue /
                          100000
                        ).toFixed(2)}
                        L
                      </strong>

                    </div>


                    <div>

                      <span>
                        Recovered
                      </span>

                      <strong>
                        ₹
                        {(
                          metrics.recovered_revenue /
                          100000
                        ).toFixed(2)}
                        L
                      </strong>

                    </div>

                  </div>

                </div>

              </div>


              {/* Summary */}

              <div className="panel summary-panel">

                <div className="panel-header">

                  <div>

                    <h3>
                      Recovery Summary
                    </h3>

                    <p>
                      Current transaction outcomes
                    </p>

                  </div>

                </div>


                <div className="summary-row">

                  <span>
                    Total Transactions
                  </span>

                  <strong>
                    {metrics.total_transactions.toLocaleString()}
                  </strong>

                </div>


                <div className="summary-row">

                  <span>
                    Failed Transactions
                  </span>

                  <strong>
                    {metrics.failed_transactions.toLocaleString()}
                  </strong>

                </div>


                <div className="summary-row">

                  <span>
                    Recovery Attempts
                  </span>

                  <strong>
                    {metrics.recovery_attempts.toLocaleString()}
                  </strong>

                </div>


                <div className="summary-row">

                  <span>
                    Stopped
                  </span>

                  <strong>
                    {metrics.stopped_transactions.toLocaleString()}
                  </strong>

                </div>

              </div>

            </section>


            {/* ============================= */}
            {/* RECENT DECISIONS              */}
            {/* ============================= */}

            <section className="panel transactions-panel">

              <div className="panel-header">

                <div>

                  <h3>
                    Recent Recovery Decisions
                  </h3>

                  <p>
                    Latest decisions generated by Revora's engine
                  </p>

                </div>


                <button
                  onClick={() =>
                    setActivePage("transactions")
                  }
                >
                  View All
                </button>

              </div>


              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>

                      <th>
                        Transaction
                      </th>

                      <th>
                        Amount
                      </th>

                      <th>
                        Status
                      </th>

                      <th>
                        Risk
                      </th>

                      <th>
                        Action
                      </th>

                      <th>
                        Recovery
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {results
                      .slice(0, 10)
                      .map((transaction) => (

                        <tr
                          key={
                            transaction.transaction_id
                          }
                        >

                          <td>

                            <strong>
                              {transaction.transaction_id}
                            </strong>

                          </td>


                          <td>

                            ₹
                            {Number(
                              transaction.amount || 0
                            ).toLocaleString("en-IN")}

                          </td>


                          <td>

                            <span
                              className={`status ${
                                (
                                  transaction.status ||
                                  ""
                                ).toLowerCase()
                              }`}
                            >
                              {transaction.status}
                            </span>

                          </td>


                          <td>

                            <span
                              className={`risk ${
                                (
                                  transaction.risk_level ||
                                  "low"
                                ).toLowerCase()
                              }`}
                            >
                              {transaction.risk_level ||
                                "LOW"}
                            </span>

                          </td>


                          <td>

                            <strong className="action">
                              {transaction.recommended_action ||
                                "STOP"}
                            </strong>

                          </td>


                          <td>
                            {transaction.recovery_status ||
                              "—"}
                          </td>

                        </tr>

                      ))}

                  </tbody>

                </table>

              </div>

            </section>

          </>

        )}

      </main>

    </div>
  );
}

export default App;