import { useEffect, useMemo, useState } from "react";

function Recovery() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  const [actionFilter, setActionFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const [actionedTransactions, setActionedTransactions] = useState({});
  const [notification, setNotification] = useState("");

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const opportunitiesPerPage = 100;

  useEffect(() => {
    async function loadRecoveryData() {
      try {
        const response = await fetch(
          "http://127.0.0.1:5000/api/results"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch recovery data");
        }

        const data = await response.json();

        setTransactions(data.results || []);
      } catch (error) {
        console.error("Failed to load recovery data:", error);
      } finally {
        setLoading(false);
      }
    }

    loadRecoveryData();
  }, []);

  /*
   * Recovery opportunities
   *
   * Show transactions where Revora
   * has recommended a recovery action.
   */
  const recoveryTransactions = useMemo(() => {
    return transactions
      .filter((transaction) => {
        const action = transaction.recommended_action;

        return (
          action === "RETRY" ||
          action === "STOP" ||
          action === "ESCALATE"
        );
      })
      .filter((transaction) => {
        const searchText = search.toLowerCase();

        const matchesSearch =
          transaction.transaction_id
            ?.toLowerCase()
            .includes(searchText) ||
          transaction.customer_id
            ?.toLowerCase()
            .includes(searchText);

        const matchesAction =
          actionFilter === "ALL" ||
          transaction.recommended_action === actionFilter;

        return matchesSearch && matchesAction;
      })
      .sort(
        (a, b) =>
          Number(b.recovery_probability || 0) -
          Number(a.recovery_probability || 0)
      );
  }, [transactions, actionFilter, search]);

  /*
   * Reset pagination whenever
   * search or filter changes.
   */
  useEffect(() => {
    setCurrentPage(1);
  }, [search, actionFilter]);

  /*
   * Overall recovery counts
   */
  const retryCount = transactions.filter(
    (transaction) =>
      transaction.recommended_action === "RETRY"
  ).length;

  const stopCount = transactions.filter(
    (transaction) =>
      transaction.recommended_action === "STOP"
  ).length;

  const escalateCount = transactions.filter(
    (transaction) =>
      transaction.recommended_action === "ESCALATE"
  ).length;

  /*
   * Pagination calculations
   */
  const totalPages = Math.ceil(
    recoveryTransactions.length / opportunitiesPerPage
  );

  const startIndex =
    (currentPage - 1) * opportunitiesPerPage;

  const endIndex =
    startIndex + opportunitiesPerPage;

  const currentRecoveryTransactions =
    recoveryTransactions.slice(
      startIndex,
      endIndex
    );

  /*
   * Page navigation
   */
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  /*
   * Execute a recovery action.
   *
   * Currently this is a frontend demo action.
   */
 const executeAction = async (transaction) => {
  try {
    setNotification(
      `Executing ${transaction.recommended_action} for ${transaction.transaction_id}...`
    );

    const response = await fetch(
      "http://127.0.0.1:5000/api/execute-recovery",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(transaction),
      }
    );

    if (!response.ok) {
      throw new Error("Recovery execution failed");
    }

    const result = await response.json();

    setActionedTransactions((previous) => ({
      ...previous,
      [transaction.transaction_id]: result,
    }));

    setNotification(
      `${result.recovery_status} — ${transaction.transaction_id}`
    );

    setTimeout(() => {
      setNotification("");
    }, 4000);

  } catch (error) {

    console.error(
      "Recovery execution failed:",
      error
    );

    setNotification(
      "Recovery execution failed. Please try again."
    );

  }
};

  /*
   * Recovery rate
   */
  const recoveryRate =
    transactions.length > 0
      ? (
          transactions.filter(
            (transaction) =>
              transaction.recovery_status === "RECOVERED"
          ).length /
          Math.max(
            transactions.filter(
              (transaction) =>
                transaction.status === "FAILED"
            ).length,
            1
          )
        ) * 100
      : 0;

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
            AI-powered decisions for recovering failed payment revenue.
          </p>
        </div>

        <div className="live-badge">
          <span></span>
          AI ENGINE ACTIVE
        </div>

      </header>


      {/* ============================= */}
      {/* KPI CARDS                     */}
      {/* ============================= */}

      <section className="metrics-grid">

        <div className="metric-card">

          <div className="metric-top">
            <p>Recoverable Revenue</p>
            <div className="metric-icon">₹</div>
          </div>

          <h2>
            ₹
            {(
              transactions
                .filter(
                  (transaction) =>
                    transaction.recommended_action !==
                    "STOP"
                )
                .reduce(
                  (sum, transaction) =>
                    sum +
                    Number(transaction.amount || 0),
                  0
                ) / 10000000
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
            <div className="metric-icon">✓</div>
          </div>

          <h2>
            ₹
            {(
              transactions
                .filter(
                  (transaction) =>
                    transaction.recovery_status ===
                    "RECOVERED"
                )
                .reduce(
                  (sum, transaction) =>
                    sum +
                    Number(transaction.amount || 0),
                  0
                ) / 10000000
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
            <div className="metric-icon">↗</div>
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
            <div className="metric-icon">⚡</div>
          </div>

          <h2>
            {retryCount.toLocaleString()}
          </h2>

          <span>
            AI retry recommendations
          </span>

        </div>

      </section>


      {/* ============================= */}
      {/* DECISION SUMMARY              */}
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


          <div className="decision-grid">

            <div className="decision-card">

              <span>RETRY</span>

              <strong>
                {retryCount.toLocaleString()}
              </strong>

              <small>
                Recovery attempts
              </small>

            </div>


            <div className="decision-card">

              <span>RECOVERED</span>

              <strong>
                {
                  transactions.filter(
                    (transaction) =>
                      transaction.recovery_status ===
                      "RECOVERED"
                  ).length.toLocaleString()
                }
              </strong>

              <small>
                Successful recoveries
              </small>

            </div>


            <div className="decision-card">

              <span>STOPPED</span>

              <strong>
                {stopCount.toLocaleString()}
              </strong>

              <small>
                No further attempts
              </small>

            </div>

          </div>

        </div>


        {/* Recovery Progress */}

        <div className="panel">

          <div className="panel-header">

            <div>
              <h3>
                Recovery Progress
              </h3>

              <p>
                Current recovery efficiency
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

          </div>

        </div>

      </section>


      {/* ============================= */}
      {/* AI RECOVERY QUEUE             */}
      {/* ============================= */}

      <section className="panel recovery-queue-panel">

        <div className="panel-header">

          <div>
            <h3>
              AI Recovery Queue
            </h3>

            <p>
              Highest-probability recovery opportunities identified by Revora.
            </p>
          </div>


          {/* Filters */}

          <div className="recovery-filters">

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


        {/* Search */}

        <div className="recovery-search">

          <input
            type="text"
            placeholder="Search transaction or customer..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

        </div>


        {/* Notification */}

        {notification && (

          <div className="recovery-notification">
            ✓ {notification}
          </div>

        )}


        {/* ============================= */}
        {/* Queue                         */}
        {/* ============================= */}

        <div className="recovery-queue">

          {currentRecoveryTransactions.length > 0 ? (

            currentRecoveryTransactions.map(
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

                const actioned =
                  actionedTransactions[
                    transaction.transaction_id
                  ];

                return (

                  <div
                    className="recovery-card"
                    key={
                      transaction.transaction_id
                    }
                  >

                    {/* Transaction */}

                    <div className="recovery-card-section">

                      <span className="small-label">
                        TRANSACTION
                      </span>

                      <strong>
                        {transaction.transaction_id}
                      </strong>

                      <span className="amount">
                        ₹
                        {Number(
                          transaction.amount || 0
                        ).toLocaleString("en-IN", {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </span>

                    </div>


                    {/* Failure */}

                    <div className="recovery-card-section">

                      <span className="small-label">
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

                    <div className="recovery-card-section">

                      <span className="small-label">
                        SCORE
                      </span>

                      <strong>
                        {score.toFixed(1)}
                      </strong>

                    </div>


                    {/* Probability */}

                    <div className="recovery-card-section probability-card">

                      <span className="small-label">
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

                    <div className="recovery-card-section">

                      <span className="small-label">
                        RISK
                      </span>

                      <span
                        className={`risk ${
                          transaction.risk_level?.toLowerCase() ||
                          ""
                        }`}
                      >
                        {transaction.risk_level ||
                          "UNKNOWN"}
                      </span>

                    </div>


                    {/* Action */}

                    <div className="recovery-card-section">

                      <span className="small-label">
                        RECOMMENDED
                      </span>

                     {actioned ? (
  <div className="action-result">

    <span className="actioned-badge">
      ✓ {actioned.recovery_status}
    </span>

    {actioned.recovered_amount > 0 && (
      <span className="recovered-amount">
        ₹
        {Number(
          actioned.recovered_amount
        ).toLocaleString("en-IN", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })} recovered
      </span>
    )}

  </div>
) : (

                        <button
  type="button"
  className="execute-action"
  onClick={() => {
    console.log("RETRY BUTTON CLICKED", transaction);
    executeAction(transaction);
  }}
>
  {transaction.recommended_action}
</button>

                      )}

                    </div>
                    {/* ============================= */}
{/* AI DECISION EXPLANATION       */}
{/* ============================= */}

<div className="ai-decision-panel">

  <div className="ai-decision-header">

    <span className="ai-label">
      🤖 AI DECISION
    </span>

    <span
      className={`ai-action-badge ${
        transaction.recommended_action?.toLowerCase() || ""
      }`}
    >
      {transaction.recommended_action}
    </span>

  </div>


  <div className="ai-reason">

    <span className="small-label">
      WHY REVORA CHOSE THIS
    </span>

    <p>
      {transaction.decision_reason ||
        "Revora evaluated the transaction and selected the most appropriate recovery action based on its recovery score, risk level, payment history, and failure reason."}
    </p>

  </div>


  {/* Decision Factors */}

  {transaction.decision_factors?.length > 0 && (

    <div className="decision-factors">

      <span className="small-label">
        DECISION FACTORS
      </span>

      <div className="factor-list">

        {transaction.decision_factors.map(
          (factor, index) => (

            <div
              className="factor-item"
              key={`${transaction.transaction_id}-factor-${index}`}
            >

              <span className="factor-name">
                {factor.factor}
              </span>

              <strong className="factor-value">
                {factor.value}
              </strong>

              <span
                className={`factor-impact ${
                  factor.impact?.toLowerCase() || ""
                }`}
              >
                {factor.impact}
              </span>

            </div>

          )
        )}

      </div>

    </div>

  )}

</div>

                  </div>

                );
              }
            )

          ) : (

            <div className="empty-recovery">

              <h3>
                No recovery opportunities found
              </h3>

              <p>
                Try changing the filter or search term.
              </p>

            </div>

          )}

        </div>


        {/* ============================= */}
        {/* Queue Footer + Pagination     */}
        {/* ============================= */}

        {recoveryTransactions.length > 0 && (

          <div className="queue-footer">

            <div>
              Showing{" "}

              <strong>
                {startIndex + 1}
              </strong>

              {" – "}

              <strong>
                {Math.min(
                  endIndex,
                  recoveryTransactions.length
                )}
              </strong>

              {" of "}

              <strong>
                {recoveryTransactions.length.toLocaleString()}
              </strong>

              {" recovery opportunities"}

              {actionFilter !== "ALL" && (
                <>
                  {" • "}
                  <strong>
                    {actionFilter}
                  </strong>
                </>
              )}
            </div>


            {/* Pagination */}

            {totalPages > 1 && (

              <div className="pagination">

                <button
                  className="pagination-btn"
                  disabled={currentPage === 1}
                  onClick={() =>
                    goToPage(currentPage - 1)
                  }
                >
                  ← Previous
                </button>


                <div className="page-numbers">

                  {Array.from(
                    {
                      length: Math.min(
                        totalPages,
                        7
                      ),
                    },
                    (_, index) => {

                      let pageNumber;

                      if (totalPages <= 7) {

                        pageNumber = index + 1;

                      } else if (
                        currentPage <= 4
                      ) {

                        pageNumber = index + 1;

                      } else if (
                        currentPage >=
                        totalPages - 3
                      ) {

                        pageNumber =
                          totalPages -
                          6 +
                          index;

                      } else {

                        pageNumber =
                          currentPage -
                          3 +
                          index;

                      }

                      return (

                        <button
                          key={pageNumber}
                          className={
                            currentPage ===
                            pageNumber
                              ? "pagination-btn active"
                              : "pagination-btn"
                          }
                          onClick={() =>
                            goToPage(
                              pageNumber
                            )
                          }
                        >
                          {pageNumber}
                        </button>

                      );

                    }
                  )}

                </div>


                <button
                  className="pagination-btn"
                  disabled={
                    currentPage === totalPages
                  }
                  onClick={() =>
                    goToPage(
                      currentPage + 1
                    )
                  }
                >
                  Next →
                </button>

              </div>

            )}

          </div>

        )}

      </section>

    </div>
  );
}

export default Recovery;