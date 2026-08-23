import { useEffect, useMemo, useState } from "react";

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const transactionsPerPage = 100;

  useEffect(() => {
    async function loadTransactions() {
      try {
        const response = await fetch(
          "http://127.0.0.1:5000/api/results"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch transactions");
        }

        const data = await response.json();

        setTransactions(data.results || []);
      } catch (error) {
        console.error("Failed to load transactions:", error);
      } finally {
        setLoading(false);
      }
    }

    loadTransactions();
  }, []);

  // Filter transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter((transaction) => {
      const searchText = search.toLowerCase();

      const matchesSearch =
        transaction.transaction_id
          ?.toLowerCase()
          .includes(searchText) ||
        transaction.customer_id
          ?.toLowerCase()
          .includes(searchText);

      const matchesStatus =
        statusFilter === "ALL" ||
        transaction.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [transactions, search, statusFilter]);

  // Reset to page 1 whenever search/filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [search, statusFilter]);

  // Pagination calculations
  const totalPages = Math.ceil(
    filteredTransactions.length / transactionsPerPage
  );

  const startIndex =
    (currentPage - 1) * transactionsPerPage;

  const endIndex =
    startIndex + transactionsPerPage;

  const currentTransactions =
    filteredTransactions.slice(
      startIndex,
      endIndex
    );

  // Page navigation
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <h2>REVORA</h2>
        <p>Loading transactions...</p>
      </div>
    );
  }

  return (
    <div className="transactions-page">

      {/* ============================= */}
      {/* Header                        */}
      {/* ============================= */}

      <div className="topbar">

        <div>
          <p className="eyebrow">
            PAYMENT INTELLIGENCE
          </p>

          <h1>
            Transactions
          </h1>

          <p className="subtitle">
            Analyze payment transactions and Revora recovery decisions.
          </p>
        </div>

        <div className="live-badge">
          <span></span>
          LIVE DATA
        </div>

      </div>


      {/* ============================= */}
      {/* Filters                       */}
      {/* ============================= */}

      <section className="panel transaction-controls">

        <div className="search-box">

          <input
            type="text"
            placeholder="Search transaction or customer..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
          />

        </div>


        <div className="filter-buttons">

          {[
            "ALL",
            "SUCCESS",
            "FAILED",
            "ABANDONED",
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

      </section>


      {/* ============================= */}
      {/* Transaction Count             */}
      {/* ============================= */}

      <div className="transaction-count">

        Showing{" "}

        <strong>
          {filteredTransactions.length === 0
            ? 0
            : startIndex + 1}
        </strong>

        {" – "}

        <strong>
          {Math.min(
            endIndex,
            filteredTransactions.length
          )}
        </strong>

        {" of "}

        <strong>
          {filteredTransactions.length.toLocaleString()}
        </strong>

        {" transactions"}

        {statusFilter !== "ALL" && (
          <>
            {" • "}
            <strong>
              {statusFilter}
            </strong>
          </>
        )}

      </div>


      {/* ============================= */}
      {/* Table                         */}
      {/* ============================= */}

      <section className="panel transactions-panel">

        <div className="table-wrapper">

          <table>

            <thead>

              <tr>

                <th>
                  Transaction
                </th>

                <th>
                  Customer
                </th>

                <th>
                  Amount
                </th>

                <th>
                  Status
                </th>

                <th>
                  Failure Reason
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

              {currentTransactions.length > 0 ? (

                currentTransactions.map(
                  (transaction) => (

                    <tr
                      key={
                        transaction.transaction_id
                      }
                    >

                      {/* Transaction */}

                      <td>
                        <strong>
                          {transaction.transaction_id}
                        </strong>
                      </td>


                      {/* Customer */}

                      <td>
                        {transaction.customer_id ||
                          "—"}
                      </td>


                      {/* Amount */}

                      <td>

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

                      </td>


                      {/* Status */}

                      <td>

                        <span
                          className={`status ${
                            transaction.status?.toLowerCase() ||
                            ""
                          }`}
                        >
                          {transaction.status}
                        </span>

                      </td>


                      {/* Failure Reason */}

                      <td>

                        {transaction.failure_reason
                          ? transaction.failure_reason.replaceAll(
                              "_",
                              " "
                            )
                          : "—"}

                      </td>


                      {/* Risk */}

                      <td>

                        <span
                          className={`risk ${
                            transaction.risk_level?.toLowerCase() ||
                            ""
                          }`}
                        >
                          {transaction.risk_level ||
                            "—"}
                        </span>

                      </td>


                      {/* Action */}

                      <td>

                        <strong className="action">
                          {transaction.recommended_action ||
                            "—"}
                        </strong>

                      </td>


                      {/* Recovery */}

                      <td>
                        {transaction.recovery_status ||
                          "—"}
                      </td>

                    </tr>

                  )
                )

              ) : (

                <tr>

                  <td
                    colSpan="8"
                    style={{
                      textAlign: "center",
                      padding: "40px",
                      color: "#6b7280",
                    }}
                  >
                    No transactions found.
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>


        {/* ============================= */}
        {/* Pagination                    */}
        {/* ============================= */}

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
                { length: Math.min(totalPages, 7) },
                (_, index) => {

                  let pageNumber;

                  if (totalPages <= 7) {
                    pageNumber = index + 1;
                  } else if (currentPage <= 4) {
                    pageNumber = index + 1;
                  } else if (
                    currentPage >=
                    totalPages - 3
                  ) {
                    pageNumber =
                      totalPages - 6 + index;
                  } else {
                    pageNumber =
                      currentPage - 3 + index;
                  }

                  return (

                    <button
                      key={pageNumber}
                      className={
                        currentPage === pageNumber
                          ? "pagination-btn active"
                          : "pagination-btn"
                      }
                      onClick={() =>
                        goToPage(pageNumber)
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
                goToPage(currentPage + 1)
              }
            >
              Next →
            </button>

          </div>

        )}

      </section>

    </div>
  );
}

export default Transactions;