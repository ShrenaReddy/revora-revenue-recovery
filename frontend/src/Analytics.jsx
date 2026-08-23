import { useEffect, useState } from "react";

function Analytics() {
  const [metrics, setMetrics] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const [metricsResponse, resultsResponse] = await Promise.all([
          fetch("http://127.0.0.1:5000/api/metrics"),
          fetch("http://127.0.0.1:5000/api/results"),
        ]);

        if (!metricsResponse.ok || !resultsResponse.ok) {
          throw new Error("Failed to fetch analytics data");
        }

        const metricsData = await metricsResponse.json();
        const resultsData = await resultsResponse.json();

        setMetrics(metricsData);
        setResults(resultsData.results || []);
      } catch (error) {
        console.error("Failed to load analytics:", error);
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>Unable to load analytics data.</p>
      </div>
    );
  }

  /* ============================= */
  /* Transaction Outcomes          */
  /* ============================= */

  const successCount = results.filter(
    (t) => t.status === "SUCCESS"
  ).length;

  const failedCount = results.filter(
    (t) => t.status === "FAILED"
  ).length;

  const abandonedCount = results.filter(
    (t) => t.status === "ABANDONED"
  ).length;

  const totalResults = results.length || 1;

  /* ============================= */
  /* AI Decision Distribution       */
  /* ============================= */

  const retryCount = results.filter(
    (t) => t.recommended_action === "RETRY"
  ).length;

  const stopCount = results.filter(
    (t) => t.recommended_action === "STOP"
  ).length;

  const escalateCount = results.filter(
    (t) => t.recommended_action === "ESCALATE"
  ).length;

  /* ============================= */
  /* Failure Reason Analysis        */
  /* ============================= */

  const failedTransactions = results.filter(
    (t) => t.status === "FAILED" || t.status === "ABANDONED"
  );

  const failureReasons = {};

  failedTransactions.forEach((transaction) => {
    const reason =
      transaction.failure_reason &&
      transaction.failure_reason !== "NONE"
        ? transaction.failure_reason
        : "UNKNOWN";

    failureReasons[reason] =
      (failureReasons[reason] || 0) + 1;
  });

  const topFailureReasons = Object.entries(failureReasons)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  const maxFailureCount =
    topFailureReasons.length > 0
      ? topFailureReasons[0][1]
      : 1;

  /* ============================= */
  /* Revenue Calculations           */
  /* ============================= */

  const recoverableRevenue =
    Number(metrics.recoverable_revenue || 0);

  const recoveredRevenue =
    Number(metrics.recovered_revenue || 0);

  const unrecoveredRevenue = Math.max(
    recoverableRevenue - recoveredRevenue,
    0
  );

  const recoverableCr =
    recoverableRevenue / 10000000;

  const recoveredCr =
    recoveredRevenue / 10000000;

  const unrecoveredCr =
    unrecoveredRevenue / 10000000;

  return (
    <div>

      {/* ============================= */}
      {/* Header                         */}
      {/* ============================= */}

      <div className="topbar">

        <div>
          <p className="eyebrow">
            BUSINESS ANALYTICS
          </p>

          <h1>Analytics</h1>

          <p className="subtitle">
            Understand payment failures and revenue recovery performance.
          </p>
        </div>

        <div className="live-badge">
          <span></span>
          AI ENGINE ACTIVE
        </div>

      </div>


      {/* ============================= */}
      {/* KPI Cards                      */}
      {/* ============================= */}

      <section className="metrics-grid">

        <div className="metric-card">

          <p>Total Transactions</p>

          <h2>
            {Number(
              metrics.total_transactions || results.length
            ).toLocaleString()}
          </h2>

          <span>
            Transactions analyzed
          </span>

        </div>


        <div className="metric-card featured">

          <p>Recovery Rate</p>

          <h2>
            {Number(metrics.recovery_rate || 0).toFixed(2)}%
          </h2>

          <span>
            Overall recovery performance
          </span>

        </div>


        <div className="metric-card">

          <p>Recoverable Revenue</p>

          <h2>
            ₹{recoverableCr.toFixed(2)}Cr
          </h2>

          <span>
            Revenue identified for recovery
          </span>

        </div>


        <div className="metric-card">

          <p>Recovered Revenue</p>

          <h2>
            ₹{recoveredCr.toFixed(2)}Cr
          </h2>

          <span>
            Successfully recovered
          </span>

        </div>

      </section>


      {/* ============================= */}
      {/* Transaction Outcomes           */}
      {/* ============================= */}

      <section className="content-grid">

        <div className="panel">

          <div className="panel-header">

            <div>
              <h3>Transaction Outcomes</h3>

              <p>
                Current payment transaction distribution
              </p>
            </div>

          </div>


          <div className="analytics-bars">

            {/* Successful */}

            <div className="analytics-row">

              <div className="analytics-label">

                <span>
                  Successful
                </span>

                <strong>
                  {successCount.toLocaleString()}
                </strong>

              </div>

              <div className="analytics-track">

                <div
                  className="analytics-fill"
                  style={{
                    width: `${
                      (successCount / totalResults) * 100
                    }%`,
                  }}
                />

              </div>

            </div>


            {/* Failed */}

            <div className="analytics-row">

              <div className="analytics-label">

                <span>
                  Failed
                </span>

                <strong>
                  {failedCount.toLocaleString()}
                </strong>

              </div>

              <div className="analytics-track">

                <div
                  className="analytics-fill"
                  style={{
                    width: `${
                      (failedCount / totalResults) * 100
                    }%`,
                  }}
                />

              </div>

            </div>


            {/* Abandoned */}

            <div className="analytics-row">

              <div className="analytics-label">

                <span>
                  Abandoned
                </span>

                <strong>
                  {abandonedCount.toLocaleString()}
                </strong>

              </div>

              <div className="analytics-track">

                <div
                  className="analytics-fill"
                  style={{
                    width: `${
                      (abandonedCount / totalResults) * 100
                    }%`,
                  }}
                />

              </div>

            </div>

          </div>

        </div>


        {/* ============================= */}
        {/* AI Decisions                   */}
        {/* ============================= */}

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                AI Decision Distribution
              </h3>

              <p>
                Actions recommended by Revora
              </p>

            </div>

          </div>


          <div className="decision-grid">

            <div className="decision-card">

              <span>
                RETRY
              </span>

              <strong>
                {retryCount.toLocaleString()}
              </strong>

            </div>


            <div className="decision-card">

              <span>
                STOP
              </span>

              <strong>
                {stopCount.toLocaleString()}
              </strong>

            </div>


            <div className="decision-card">

              <span>
                ESCALATE
              </span>

              <strong>
                {escalateCount.toLocaleString()}
              </strong>

            </div>

          </div>

        </div>

      </section>


      {/* ============================= */}
      {/* Failure Analysis               */}
      {/* ============================= */}

      <section className="panel analytics-panel">

        <div className="panel-header">

          <div>

            <h3>
              Failure Reason Analysis
            </h3>

            <p>
              Most common reasons behind payment failures
            </p>

          </div>

        </div>


        <div className="failure-analysis">

          {topFailureReasons.length === 0 ? (

            <p>
              No failed transactions available.
            </p>

          ) : (

            topFailureReasons.map(
              ([reason, count]) => (

                <div
                  className="failure-analysis-row"
                  key={reason}
                >

                  <div className="failure-analysis-label">

                    <span>
                      {reason.replaceAll("_", " ")}
                    </span>

                    <strong>
                      {count.toLocaleString()}
                    </strong>

                  </div>

                  <div className="analytics-track">

                    <div
                      className="analytics-fill"
                      style={{
                        width: `${
                          (count / maxFailureCount) * 100
                        }%`,
                      }}
                    />

                  </div>

                </div>

              )
            )

          )}

        </div>

      </section>


      {/* ============================= */}
      {/* Revenue Intelligence           */}
      {/* ============================= */}

      <section className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Revenue Intelligence
            </h3>

            <p>
              Financial impact identified by Revora
            </p>

          </div>

        </div>


        <div className="revenue-analysis">

          <div>

            <span>
              Recoverable Revenue
            </span>

            <strong>
              ₹{recoverableCr.toFixed(2)}Cr
            </strong>

          </div>


          <div>

            <span>
              Recovered Revenue
            </span>

            <strong>
              ₹{recoveredCr.toFixed(2)}Cr
            </strong>

          </div>


          <div>

            <span>
              Unrecovered Opportunity
            </span>

            <strong>
              ₹{unrecoveredCr.toFixed(2)}Cr
            </strong>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Analytics;