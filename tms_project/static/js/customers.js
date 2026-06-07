let currentRow = null;


/* ROW CLICK */
document.addEventListener("click", function (e) {

    const row = e.target.closest("tbody tr");

    if (!row) return;

    currentRow = row;

    openCustomerPanel(row);

});


/* OPEN PANEL */
function openCustomerPanel(row) {

    document
        .getElementById("customerPanel")
        .classList
        .remove("hidden");


    document.getElementById("cTitle").innerText =
        row.dataset.id + " Details";

    document.getElementById("cCompany").innerText =
        row.dataset.company;

    document.getElementById("cContact").innerText =
        row.dataset.contact || "N/A";

    document.getElementById("cPhone").innerText =
        row.dataset.phone || "---";

    document.getElementById("cCategory").innerText =
        row.dataset.category;

    document.getElementById("cCnic").innerText =
        row.dataset.cnic || "---";

    document.getElementById("cAddress").innerText =
        row.dataset.address || "---";

    document.getElementById("cNotes").innerText =
        row.dataset.notes || "---";

    const balanceElement = document.getElementById("cBalance");
    const statusElement = document.getElementById("cStatus");

balanceElement.innerText =
    "Rs. " + row.dataset.balance;


balanceElement.classList.remove(
    "due-badge",
    "advance-badge",
    "clear-badge"
);


/* ADD NEW CLASS */
const balanceStatus = row.dataset.balanceStatus;

if (balanceStatus === "Due") {

    balanceElement.classList.add("due-badge");

}
else if (balanceStatus === "Advance") {

    balanceElement.classList.add("advance-badge");

}
else {

    balanceElement.classList.add("clear-badge");

}

    document.getElementById("cStatus").innerText =
        row.dataset.balanceStatus;
}


/* CLOSE PANEL */
function closeCustomer() {

    document
        .getElementById("customerPanel")
        .classList
        .add("hidden");
}


/* OPEN EDIT MODAL */
function openEditModal() {

    if (!currentRow) return;

    const customerId = currentRow.dataset.customerId;

    document
        .getElementById("editCustomerForm")
        .action = `/tms/customers/edit/${customerId}/`;

    document
        .getElementById("editModal")
        .classList
        .remove("hidden");


    document.getElementById("editCompany").value =
    currentRow.dataset.company;

document.getElementById("editContact").value =
    currentRow.dataset.contact;

document.getElementById("editPhone").value =
    currentRow.dataset.phone;

document.getElementById("editCnic").value =
    currentRow.dataset.cnic;

document.getElementById("editAddress").value =
    currentRow.dataset.address;

document.getElementById("editNotes").value =
    currentRow.dataset.notes;

document.getElementById("editCategory").value =
    currentRow.dataset.category;


}


/* CLOSE MODAL */
function closeEditModal() {

    document
        .getElementById("editModal")
        .classList
        .add("hidden");
}