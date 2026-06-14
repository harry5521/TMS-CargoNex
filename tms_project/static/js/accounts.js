// ======================================
// RIGHT PANEL
// ======================================

let currentRow = null;

document.addEventListener("click", function (e) {

    const row = e.target.closest("tbody tr");

    if (!row) return;

    currentRow = row;

    openTransactionPanel(row);

});


function openTransactionPanel(row) {

    document
        .getElementById("txnPanel")
        .classList
        .remove("hidden");

    
    document.getElementById("txnTitle").innerText =
        row.dataset.txnId;

    document.getElementById("txnDate").innerText =
        row.dataset.date;

    document.getElementById("txnCategory").innerText =
        row.dataset.category;

    document.getElementById("txnType").innerText =
        row.dataset.type;

    document.getElementById("txnAmount").innerText =
        "PKR " + row.dataset.amount;

    document.getElementById("txnCustomer").innerText =
        row.dataset.customer || "-";

    document.getElementById("txnBuilty").innerText =
        row.dataset.builty || "-";

    document.getElementById("txnRemarks").innerText =
        row.dataset.remarks || "-";
}


function closeTxn() {

    document
        .getElementById("txnPanel")
        .classList
        .add("hidden");
}



// ======================================
// CATEGORY MODAL
// ======================================

function openCategoryModal() {

    document
        .getElementById("categoryModal")
        .classList
        .remove("hidden");
}


function closeCategoryModal() {

    document
        .getElementById("categoryModal")
        .classList
        .add("hidden");
}



// ======================================
// TRANSACTION MODAL
// ======================================

function openTransactionModal() {

    document
        .getElementById("transactionModal")
        .classList
        .remove("hidden");
}


function closeTransactionModal() {

    document
        .getElementById("transactionModal")
        .classList
        .add("hidden");
}



// ======================================
// ADD BULK ROW
// ======================================

function addTransactionRow() {

    const container =
        document.getElementById(
            "transactionRows"
        );

    const row =
        document.createElement("div");

    row.className =
        "transaction-row";

    row.innerHTML = `

        <button
            type="button"
            class="remove-row-btn"
            onclick="removeTransactionRow(this)"
        >
            ✖
        </button>

        <select>

            <option value="cash_in">
                Cash In
            </option>

            <option value="cash_out">
                Cash Out
            </option>

        </select>

        <select>

            <option>
                Select Category
            </option>

        </select>

        <input
            class="full-width"
            type="number"
            placeholder="Amount"
        >

        <input
            class="full-width"
            type="text"
            placeholder="Remarks"
        >
    `;

    container.appendChild(row);
}

function removeTransactionRow(button) {

    const container =
        document.getElementById(
            "transactionRows"
        );

    const rows =
        container.querySelectorAll(
            ".transaction-row"
        );

    // Keep at least one row

    if (rows.length === 1) {
        return;
    }

    button
        .closest(".transaction-row")
        .remove();
}


// ======================================
// CLOSE MODAL ON BACKDROP CLICK
// ======================================

document.addEventListener("click", function (e) {

    if (
        e.target.id === "categoryModal"
    ) {

        closeCategoryModal();
    }

    if (
        e.target.id === "transactionModal"
    ) {

        closeTransactionModal();
    }

});