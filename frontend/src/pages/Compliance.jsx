import { useCallback, useEffect, useMemo, useState } from "react";

function Compliance() {
  const [auditRecords, setAuditRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  /*
   * ==========================================
   * LOAD AUDIT DATA
   * ==========================================
   */

  const loadAuditData = useCallback(async (showRefresh = false) => {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const response = await fetch(
        "http://127.0.0.1:5000/api/audit"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch audit records");
      }

      const data = await response.json();

      setAuditRecords(data.audit || []);
    } catch (error) {
      console.error(
        "Failed to load audit records:",
        error
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  /*
   * Load audit records when page opens
   */

  useEffect(() => {
    loadAuditData();
  }, [loadAuditData]);

  /*
   * ==========================================
   * FILTER + SORT AUDIT RECORDS
   * ==========================================
   */

  const filteredRecords = useMemo(() => {
    const searchText = search
      .trim()
      .toLowerCase();

    return [...auditRecords]
      .filter((record) => {
        const transactionId =
          record.transaction_id
            ?.toLowerCase() || "";

        const customerId =
          record.customer_id
            ?.toLowerCase() || "";

        const failureReason =
          record.failure_reason
            ?.toLowerCase()
            .replaceAll("_", " ") || "";

        const action =
          record.recommended_action
            ?.toLowerCase() || "";

        const matchesSearch =
          !searchText ||
          transactionId.includes(searchText) ||
          customerId.includes(searchText) ||
          failureReason.includes(searchText) ||
          action.includes(searchText);

        const matchesStatus =
          statusFilter === "ALL" ||
          record.recovery_status === statusFilter;

        return (
          matchesSearch &&
          matchesStatus
        );
      })
      .sort((a, b) => {
        const timeA = new Date(
          a.audit_timestamp || 0
        ).getTime();

        const timeB = new Date(
          b.audit_timestamp || 0
        ).getTime();

        return timeB - timeA;
      });
  }, [
    auditRecords,
    search,
    statusFilter
  ]);

  /*
   * ==========================================
   * COMPLIANCE STATISTICS
   * ==========================================
   */

  const totalActions =
    auditRecords.length;

  const recoveredCount =
    auditRecords.filter(
      (record) =>
        record.recovery_status ===
        "RECOVERED"
    ).length;

  const escalatedCount =
    auditRecords.filter(
      (record) =>
        record.recovery_status ===
        "ESCALATED"
    ).length;

  const stoppedCount =
    auditRecords.filter(
      (record) =>
        record.recovery_status ===
        "STOPPED"
    ).length;

  const failedCount =
    auditRecords.filter(
      (record) =>
        record.recovery_status ===
        "FAILED"
    ).length;

  /*
   * ==========================================
   * RECOVERED REVENUE
   * ==========================================
   */

  const recoveredRevenue =
    auditRecords.reduce(
      (sum, record) =>
        sum +
        Number(
          record.recovered_amount || 0
        ),
      0
    );

  /*
   * ==========================================
   * ACTION EXECUTION RATE
   * ==========================================
   */

  const executedActions =
    auditRecords.filter(
      (record) =>
        String(
          record.action_executed
        ).toLowerCase() === "true"
    ).length;

  const executionRate =
    totalActions > 0
      ? (
          (executedActions /
            totalActions) *
          100
        ).toFixed(0)
      : "0";

  /*
   * ==========================================
   * FORMAT CURRENCY
   * ==========================================
   */

  const formatCurrency = (value) => {
    return Number(value || 0).toLocaleString(
      "en-IN",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    );
  };

  /*
   * ==========================================
   * LOADING
   * ==========================================
   */

  if (loading) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>
          Loading compliance intelligence...
        </p>
      </div>
    );
  }

  /*
   * ==========================================
   * PAGE
   * ==========================================
   */

  return (
    <div className="compliance-page">

      {/* ================================= */}
      {/* HEADER                            */}
      {/* ================================= */}

      <header className="topbar">

        <div>

          <p className="eyebrow">
            GOVERNANCE & COMPLIANCE
          </p>

          <h1>
            Compliance & Audit
          </h1>

          <p className="subtitle">
            Complete traceable record of Revora
            recovery decisions and actions.
          </p>

        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}
        >

          <button
            type="button"
            onClick={() =>
              loadAuditData(true)
            }
            disabled={refreshing}
            style={{
              padding: "9px 14px",
              borderRadius: "8px",
              border: "1px solid #d1d5db",
              background: "#ffffff",
              cursor: refreshing
                ? "not-allowed"
                : "pointer",
              fontWeight: "600"
            }}
          >
            {refreshing
              ? "Refreshing..."
              : "↻ Refresh Audit"}
          </button>

          <div className="live-badge">
            <span></span>
            AUDIT LOG ACTIVE
          </div>

        </div>

      </header>


      {/* ================================= */}
      {/* KPI CARDS                         */}
      {/* ================================= */}

      <section className="metrics-grid">

        {/* Total Actions */}

        <div className="metric-card">

          <div className="metric-top">

            <p>
              Total Actions
            </p>

            <div className="metric-icon">
              #
            </div>

          </div>

          <h2>
            {totalActions.toLocaleString()}
          </h2>

          <span>
            Recorded recovery actions
          </span>

        </div>


        {/* Recovered */}

        <div className="metric-card featured">

          <div className="metric-top">

            <p>
              Recovered
            </p>

            <div className="metric-icon">
              ✓
            </div>

          </div>

          <h2>
            {recoveredCount.toLocaleString()}
          </h2>

          <span>
            Successful recovery actions
          </span>

        </div>


        {/* Escalated */}

        <div className="metric-card">

          <div className="metric-top">

            <p>
              Escalated
            </p>

            <div className="metric-icon">
              !
            </div>

          </div>

          <h2>
            {escalatedCount.toLocaleString()}
          </h2>

          <span>
            Manual review actions
          </span>

        </div>


        {/* Recovered Revenue */}

        <div className="metric-card">

          <div className="metric-top">

            <p>
              Recovered Revenue
            </p>

            <div className="metric-icon">
              ₹
            </div>

          </div>

          <h2>
            ₹
            {(
              recoveredRevenue /
              100000
            ).toFixed(2)}
            L
          </h2>

          <span>
            Revenue recovered through actions
          </span>

        </div>

      </section>


      {/* ================================= */}
      {/* COMPLIANCE OVERVIEW               */}
      {/* ================================= */}

      <section className="content-grid">

        {/* Overview */}

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Compliance Overview
              </h3>

              <p>
                Every recovery action is recorded
                for traceability and review.
              </p>

            </div>

          </div>


          <div className="decision-grid">

            {/* Recovered */}

            <div className="decision-card">

              <span>
                RECOVERED
              </span>

              <strong>
                {recoveredCount}
              </strong>

              <small>
                Successful actions
              </small>

            </div>


            {/* Escalated */}

            <div className="decision-card">

              <span>
                ESCALATED
              </span>

              <strong>
                {escalatedCount}
              </strong>

              <small>
                Manual review required
              </small>

            </div>


            {/* Stopped */}

            <div className="decision-card">

              <span>
                STOPPED
              </span>

              <strong>
                {stoppedCount}
              </strong>

              <small>
                Further recovery blocked
              </small>

            </div>

          </div>

        </div>


        {/* ================================= */}
        {/* AUDIT CONTROLS                    */}
        {/* ================================= */}

        <div className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Audit Controls
              </h3>

              <p>
                Search and filter recovery events.
              </p>

            </div>

          </div>


          <div className="recovery-search">

            <input
              type="text"
              placeholder="Search transaction, customer, action..."
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
            />

          </div>


          <div className="recovery-filters">

            {[
              "ALL",
              "RECOVERED",
              "ESCALATED",
              "STOPPED",
              "FAILED"
            ].map((status) => (

              <button
                key={status}
                className={
                  statusFilter === status
                    ? "filter-btn active"
                    : "filter-btn"
                }
                onClick={() =>
                  setStatusFilter(status)
                }
              >
                {status}
              </button>

            ))}

          </div>

        </div>

      </section>


      {/* ================================= */}
      {/* AUDIT HEALTH                      */}
      {/* ================================= */}

      <section className="panel">

        <div className="panel-header">

          <div>

            <h3>
              Audit Health
            </h3>

            <p>
              Operational visibility into recorded
              recovery actions.
            </p>

          </div>

        </div>


        <div className="decision-grid">

          <div className="decision-card">

            <span>
              EXECUTED
            </span>

            <strong>
              {executedActions}
            </strong>

            <small>
              Actions actually processed
            </small>

          </div>


          <div className="decision-card">

            <span>
              EXECUTION RATE
            </span>

            <strong>
              {executionRate}%
            </strong>

            <small>
              Actions successfully processed
            </small>

          </div>


          <div className="decision-card">

            <span>
              FAILED
            </span>

            <strong>
              {failedCount}
            </strong>

            <small>
              Recovery attempts that failed
            </small>

          </div>

        </div>

      </section>


      {/* ================================= */}
      {/* AUDIT LOG                         */}
      {/* ================================= */}

      <section className="panel audit-panel">

        <div className="panel-header">

          <div>

            <h3>
              Recovery Audit Log
            </h3>

            <p>
              Traceable record of recovery decisions,
              actions, outcomes and controls.
            </p>

          </div>

          <div className="audit-count">

            Showing{" "}

            <strong>
              {filteredRecords.length}
            </strong>

            {" "}events

          </div>

        </div>


        <div className="audit-list">

          {filteredRecords.length > 0 ? (

            filteredRecords.map(
              (record, index) => {

                const probability =
                  Number(
                    record.recovery_probability ||
                    0
                  ) * 100;

                const recoveredAmount =
                  Number(
                    record.recovered_amount ||
                    0
                  );

                const executed =
                  String(
                    record.action_executed
                  ).toLowerCase() ===
                  "true";

                return (

                  <div
                    className="audit-card"
                    key={
                      `${record.transaction_id}-${record.audit_timestamp}-${index}`
                    }
                  >

                    {/* ========================= */}
                    {/* MAIN AUDIT INFORMATION     */}
                    {/* ========================= */}

                    <div className="audit-main">

                      <span className="small-label">
                        TRANSACTION
                      </span>

                      <strong>
                        {record.transaction_id}
                      </strong>

                      <span className="audit-customer">
                        {record.customer_id}
                      </span>

                    </div>


                    {/* Action */}

                    <div className="audit-field">

                      <span className="small-label">
                        ACTION
                      </span>

                      <strong>
                        {record.recommended_action ||
                          "UNKNOWN"}
                      </strong>

                    </div>


                    {/* Status */}

                    <div className="audit-field">

                      <span className="small-label">
                        STATUS
                      </span>

                      <span
                        className={`audit-status ${
                          record.recovery_status
                            ?.toLowerCase() ||
                          ""
                        }`}
                      >
                        {record.recovery_status ||
                          "UNKNOWN"}
                      </span>

                    </div>


                    {/* Amount */}

                    <div className="audit-field">

                      <span className="small-label">
                        AMOUNT
                      </span>

                      <strong>
                        ₹
                        {formatCurrency(
                          record.amount
                        )}
                      </strong>

                    </div>


                    {/* Probability */}

                    <div className="audit-field">

                      <span className="small-label">
                        PROBABILITY
                      </span>

                      <strong>
                        {probability.toFixed(0)}%
                      </strong>

                    </div>


                    {/* Audit Time */}

                    <div className="audit-field">

                      <span className="small-label">
                        AUDIT TIME
                      </span>

                      <strong>
                        {record.audit_timestamp ||
                          "N/A"}
                      </strong>

                    </div>


                    {/* ========================= */}
                    {/* DETAILS                    */}
                    {/* ========================= */}

                    <div className="audit-details">

                      <div className="audit-detail-grid">

                        {/* Recovery Score */}

                        <div>

                          <span className="small-label">
                            RECOVERY SCORE
                          </span>

                          <strong>
                            {Number(
                              record.recovery_score ||
                              0
                            ).toFixed(1)}
                            /100
                          </strong>

                        </div>


                        {/* Attempts */}

                        <div>

                          <span className="small-label">
                            ATTEMPTS
                          </span>

                          <strong>
                            {record.attempts_before ??
                              0}
                            {" → "}
                            {record.attempts_after ??
                              0}
                          </strong>

                        </div>


                        {/* Risk */}

                        <div>

                          <span className="small-label">
                            RISK
                          </span>

                          <strong>
                            {record.risk_level ||
                              "UNKNOWN"}
                          </strong>

                        </div>


                        {/* Failure Reason */}

                        <div>

                          <span className="small-label">
                            FAILURE REASON
                          </span>

                          <strong>
                            {record.failure_reason
                              ? record.failure_reason.replaceAll(
                                  "_",
                                  " "
                                )
                              : "UNKNOWN"}
                          </strong>

                        </div>


                        {/* Recovered Amount */}

                        <div>

                          <span className="small-label">
                            RECOVERED AMOUNT
                          </span>

                          <strong>
                            ₹
                            {formatCurrency(
                              recoveredAmount
                            )}
                          </strong>

                        </div>


                        {/* Action Executed */}

                        <div>

                          <span className="small-label">
                            ACTION EXECUTED
                          </span>

                          <strong>
                            {executed
                              ? "YES"
                              : "NO"}
                          </strong>

                        </div>

                      </div>


                      {/* ========================= */}
                      {/* AI DECISION REASON         */}
                      {/* ========================= */}

                      <div className="audit-reason">

                        <span className="small-label">
                          AI DECISION REASON
                        </span>

                        <p>
                          {record.decision_reason ||
                            "No decision reasoning recorded."}
                        </p>

                      </div>


                      {/* ========================= */}
                      {/* STOPPING RULE              */}
                      {/* ========================= */}

                      <div className="audit-rule">

                        <span className="small-label">
                          🛡️ STOPPING RULE
                        </span>

                        <p>
                          {record.stopping_rule ||
                            "No stopping rule recorded."}
                        </p>

                      </div>

                    </div>

                  </div>

                );
              }
            )

          ) : (

            <div className="empty-recovery">

              <h3>
                No audit records found
              </h3>

              <p>
                Execute a recovery action or
                change the search/filter.
              </p>

            </div>

          )}

        </div>

      </section>

    </div>
  );
}

export default Compliance;