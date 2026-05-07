const expensesData = {
  "EXP-001": {
    date: "2023-10-24",
    category: "Vehicle",
    ref: "LP-9920",
    amount: "45,200",
    payment: "Credit",
    status: "Pending"
  },
  "EXP-002": {
    date: "2023-10-24",
    category: "Office",
    ref: "BILL-221",
    amount: "1,250",
    payment: "Cash",
    status: "Paid"
  }
};

let currentExpenseId = null;

/* SELECT EXPENSE */
function selectExpense(id) {
  const e = expensesData[id];
  if (!e) return;

  currentExpenseId = id;

  document.getElementById("expensePanel").classList.remove("hidden");

  document.getElementById("expTitle").innerText = id + " Details";
  document.getElementById("expDate").innerText = e.date;
  document.getElementById("expCategory").innerText = e.category;
  document.getElementById("expRef").innerText = e.ref;
  document.getElementById("expAmount").innerText = e.amount;
  document.getElementById("expPayment").innerText = e.payment;
  document.getElementById("expStatus").innerText = e.status;
}

/* CLOSE PANEL */
function closeExpense() {
  document.getElementById("expensePanel").classList.add("hidden");
}

/* OPEN MODAL */
function openEditModal() {
  const e = expensesData[currentExpenseId];

  document.getElementById("editModal").classList.remove("hidden");

  document.getElementById("editDate").value = e.date;
  document.getElementById("editCategory").value = e.category;
  document.getElementById("editRef").value = e.ref;
  document.getElementById("editAmount").value = e.amount;
  document.getElementById("editPayment").value = e.payment;
  document.getElementById("editStatus").value = e.status;
}

/* CLOSE MODAL */
function closeEditModal() {
  document.getElementById("editModal").classList.add("hidden");
}

/* SAVE EDIT */
function saveEdit() {

  const e = expensesData[currentExpenseId];

  e.date = document.getElementById("editDate").value;
  e.category = document.getElementById("editCategory").value;
  e.ref = document.getElementById("editRef").value;
  e.amount = document.getElementById("editAmount").value;
  e.payment = document.getElementById("editPayment").value;
  e.status = document.getElementById("editStatus").value;

  // Update panel
  selectExpense(currentExpenseId);

  // Update table
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach(row => {
    const id = row.querySelector(".link").innerText;

    if (id === currentExpenseId) {
      row.cells[1].innerText = e.date;
      row.cells[2].innerText = e.category;
      row.cells[3].innerText = e.ref;
      row.cells[4].innerText = e.amount;
      row.cells[5].innerText = e.payment;
      row.cells[6].innerText = e.status;
    }
  });

  closeEditModal();
}