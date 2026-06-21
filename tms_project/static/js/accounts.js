// ======================================
// RIGHT PANEL
// ======================================

let currentRow = null;

document.addEventListener("click", function (e) {

    const row =
        e.target.closest(
            "#txnBody tr"
        );

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

    document.getElementById("txnId").innerText =
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
        row.dataset.remarks || "No remarks";
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

function editCategory(
    id,
    name
) {

    document
        .getElementById("categoryId")
        .value = id;

    document
        .getElementById("categoryName")
        .value = name;

    document
        .getElementById("categorySubmitBtn")
        .innerText = "Update";

    document
        .getElementById("categoryName")
        .focus();
}


function closeCategoryModal() {

    document
        .getElementById("categoryModal")
        .classList
        .add("hidden");

    document
        .getElementById("categoryId")
        .value = "";

    document
        .getElementById("categoryName")
        .value = "";

    document
        .getElementById("categorySubmitBtn")
        .innerText = "Add";
}


// Save Category using Ajax
document
    .getElementById("categoryForm")
    .addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            const formData =
                new FormData(this);

            const response =
                await fetch(
                    "/tms/accounts/categories/save/",
                    {
                        method: "POST",
                        body: formData,
                        headers: {
                            "X-CSRFToken":
                                document.querySelector(
                                    "[name=csrfmiddlewaretoken]"
                                ).value
                        }
                    }
                );

            const data =
                await response.json();

            if (data.success) {

    localStorage.setItem(
        "reopenCategoryModal",
        "true"
    );

    window.location.reload();
}
        }
    );

window.addEventListener(
    "load",
    function () {

        if (
            localStorage.getItem(
                "reopenCategoryModal"
            ) === "true"
        ) {

            openCategoryModal();

            localStorage.removeItem(
                "reopenCategoryModal"
            );
        }

    }
);


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

        <select name="transaction_type">

            <option value="cash_in">
                Cash In
            </option>

            <option value="cash_out">
                Cash Out
            </option>

        </select>

        <select name="category">

            <option value="">
                Select Category
            </option>

            ${window.categoryOptions || ""}

        </select>

        <input
            class="full-width"
            type="number"
            step="0.01"
            name="amount"
            placeholder="Amount"
            required
        >

        <input
            class="full-width"
            type="text"
            name="remarks"
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

