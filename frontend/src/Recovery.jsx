import { useEffect, useMemo, useState } from "react";

function Recovery() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("ALL");

  useEffect(() => {
    async function loadRecoveryData() {
      try {
        const response = await fetch(
          "http://127.0.0.1:5000/api/results"
        );

        if (!response.ok) {
          throw new Error("Failed to load recovery data");
        }

        const data = await response.json();

        setTransactions(data.results || []);
      } catch (error) {
        console.error(
          "Failed to load recovery data:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadRecoveryData();
  }, []);

  /* ============================= */
  /* Recovery calculations          */
  /* ============================= */

  const failedTransactions = useMemo(
    () =>
      transactions.filter(
        (transaction) =>
          transaction.status === "FAILED" ||
          transaction.status === "ABANDONED"
      ),
    [transactions]
  );

  const recoveryAttempts = useMemo(
    () =>
      transactions.filter(
        (transaction) =>
          transaction.recommended_action === "RETRY"
      ),
    [transactions]
  );

  const recoveredTransactions = useMemo(
    () =>
      transactions.filter(
        (transaction) =>
          transaction.recovery_status === "RECOVERED"
      ),
    [transactions]
  );

  const stoppedTransactions = useMemo(
    () =>
      transactions.filter(
        (transaction) =>
          transaction.recovery_status === "STOPPED"
      ),
    [transactions]
  );

  const recoverableRevenue = failedTransactions.reduce(
    (sum, transaction) =>
      sum + Number(transaction.amount || 0),
    0
  );

  const recoveredRevenue = recoveredTransactions.reduce(
    (sum, transaction) =>
      sum + Number(transaction.recovered_amount || 0),
    0
  );

  const recoveryRate =
    recoverableRevenue > 0
      ? (recoveredRevenue / recoverableRevenue) * 100
      : 0;

  /* ============================= */
  /* Recovery queue                */
  /* ============================= */

  const recoveryQueue = useMemo(() => {
    return [...failedTransactions]
      .sort(
        (a, b) =>
          Number(b.recovery_probability || 0) -
          Number(a.recovery_probability || 0)
      )
      .filter((transaction) => {
        if (actionFilter === "ALL") {
          return true;
        }

        return (
          transaction.recommended_action ===
          actionFilter
        );
      })
      .slice(0, 50);
  }, [failedTransactions, actionFilter]);

  /* ============================= */
  /* Loading                       */
  /* ============================= */

  if (loading) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>Loading recovery intelligence...</p>
      </div>
    );
  }

  return (
    <div className="recovery-page">

      {/* ============================= */}
      {/* Header                        */}
      {/* ============================= */}

      <header className="topbar">

        <div>

          <p className="eyebrow">
            AI REVENUE RECOVERY
          </p>

          <h1>
            Recovery Intelligence
          </h1>

          <p className="subtitle">
            AI-powered decisions for recovering failed
            payment revenue.
          </p>

        </div>

        <div className="live-badge">
          <span></span>
          AI ENGINE ACTIVE
        </div>

      </header>


      {/* ============================= */}
      {/* KPI Cards                     */}
      {/* ============================= */}

      <section className="metrics-grid recovery-kpis">

        <div className="metric-card">

          <div className="metric-top">
            <p>Recoverable Revenue</p>

            <div className="metric-icon">
              ₹
            </div>
          </div>

          <h2>
            ₹
            {(
              recoverableRevenue / 10000000
            ).toFixed(2)}
            Cr
          </h2>

          <span>
            Revenue identified for recovery
          </span>

        </div>


        <div className="metric-card featured">

          <div className="metric-top">
            <p>Recovered Revenue</p>

            <div className="metric-icon">
              ✓
            </div>
          </div>

          <h2>
            ₹
            {(
              recoveredRevenue / 10000000
            ).toFixed(2)}
            Cr
          </h2>

          <span>
            Successfully recovered
          </span>

        </div>


        <div className="metric-card">

          <div className="metric-top">
            <p>Recovery Rate</p>

            <div className="metric-icon">
              ↗
            </div>
          </div>

          <h2>
            {recoveryRate.toFixed(2)}%
          </h2>

          <span>
            Revenue recovery efficiency
          </span>

        </div>


        <div className="metric-card">

          <div className="metric-top">
            <p>Recovery Attempts</p>

            <div className="metric-icon">
              ⚡
            </div>
          </div>

          <h2>
            {recoveryAttempts.length.toLocaleString()}
          </h2>

          <span>
            AI retry recommendations
          </span>

        </div>

      </section>


      {/* ============================= */}
      {/* Decision Summary              */}
      {/* ============================= */}

      <section className="content-grid">

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Recovery Decision Summary
              </h3>

              <p>
                How Revora is handling failed payments
              </p>

            </div>

          </div>


          <div className="decision-summary-grid">

            <div className="decision-box retry">

              <span>
                RETRY
              </span>

              <strong>
                {recoveryAttempts.length.toLocaleString()}
              </strong>

              <small>
                Recovery attempts
              </small>

            </div>


            <div className="decision-box recovered">

              <span>
                RECOVERED
              </span>

              <strong>
                {recoveredTransactions.length.toLocaleString()}
              </strong>

              <small>
                Successful recoveries
              </small>

            </div>


            <div className="decision-box stopped">

              <span>
                STOPPED
              </span>

              <strong>
                {stoppedTransactions.length.toLocaleString()}
              </strong>

              <small>
                No further attempts
              </small>

            </div>

          </div>

        </div>


        {/* Recovery progress */}

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Recovery Progress
              </h3>

              <p>
                Recovered versus recoverable revenue
              </p>

            </div>

          </div>


          <div className="recovery-display">

            <div className="recovery-number">
              {recoveryRate.toFixed(1)}%
            </div>

            <p>
              Revenue recovered
            </p>


            <div className="progress-track">

              <div
                className="progress-fill"
                style={{
                  width: `${Math.min(
                    recoveryRate,
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
                    recoverableRevenue / 10000000
                  ).toFixed(2)}
                  Cr
                </strong>

              </div>


              <div>

                <span>
                  Recovered
                </span>

                <strong>
                  ₹
                  {(
                    recoveredRevenue / 10000000
                  ).toFixed(2)}
                  Cr
                </strong>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* ============================= */}
      {/* AI Recovery Queue             */}
      {/* ============================= */}

      <section className="panel recovery-queue-panel">

        <div className="panel-header recovery-queue-header">

          <div>

            <h3>
              AI Recovery Queue
            </h3>

            <p>
              Highest-probability recovery opportunities
              identified by Revora.
            </p>

          </div>


          <div className="filter-buttons">

            {[
              "ALL",
              "RETRY",
              "STOP",
              "ESCALATE",
            ].map((action) => (

              <button
                key={action}
                className={
                  actionFilter === action
                    ? "filter-btn active"
                    : "filter-btn"
                }
                onClick={() =>
                  setActionFilter(action)
                }
              >
                {action}
              </button>

            ))}

          </div>

        </div>


        <div className="recovery-list">

          {recoveryQueue.length === 0 ? (

            <div className="empty-recovery">
              No recovery opportunities found.
            </div>

          ) : (

            recoveryQueue.map(
              (transaction) => {

                const probability =
                  Number(
                    transaction.recovery_probability ||
                    0
                  ) * 100;

                const score =
                  Number(
                    transaction.recovery_score || 0
                  );

                return (

                  <div
                    className="recovery-item"
                    key={
                      transaction.transaction_id
                    }
                  >

                    {/* Transaction */}

                    <div className="recovery-item-main">

                      <span className="transaction-label">
                        TRANSACTION
                      </span>

                      <h4>
                        {transaction.transaction_id}
                      </h4>

                      <strong>
                        ₹
                        {Number(
                          transaction.amount || 0
                        ).toLocaleString(
                          "en-IN",
                          {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          }
                        )}
                      </strong>

                    </div>


                    {/* Failure */}

                    <div className="recovery-item-column">

                      <span>
                        FAILURE
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


                    {/* Score */}

                    <div className="recovery-item-column">

                      <span>
                        SCORE
                      </span>

                      <strong>
                        {score.toFixed(1)}
                      </strong>

                    </div>


                    {/* Probability */}

                    <div className="recovery-item-column probability-column">

                      <span>
                        PROBABILITY
                      </span>

                      <strong>
                        {probability.toFixed(0)}%
                      </strong>

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


                    {/* Risk */}

                    <div className="recovery-item-column">

                      <span>
                        RISK
                      </span>

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

                    </div>


                    {/* Action */}

                    <div className="recovery-action">

                      <span>
                        RECOMMENDED
                      </span>

                      <strong>
                        {transaction.recommended_action ||
                          "STOP"}
                      </strong>

                    </div>

                  </div>

                );
              }
            )

          )}

        </div>

      </section>

    </div>
  );
}

export default Recovery;