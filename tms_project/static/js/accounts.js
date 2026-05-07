const transactions = {
  "TXN-8821": {
    date: "2024-05-20",
    type: "Payment",
    source: "Client",
    ref: "INV-5502",
    amount: "+₹45,000",
    balance: "₹1,25,400"
  },
  "TXN-8822": {
    date: "2024-05-18",
    type: "Expense",
    source: "Trip Expense",
    ref: "TRIP-990",
    amount: "-₹12,000",
    balance: "₹1,13,400"
  }
};

let currentTxnId = null;

/* ROW CLICK */
document.addEventListener("click", function(e){
  const row = e.target.closest("tr");

  if (row) {
    const link = row.querySelector(".link");
    if (link) {
      selectTxn(link.dataset.id);
    }
  }
});

function selectTxn(id){
  const t = transactions[id];
  if(!t) return;

  currentTxnId = id;

  document.getElementById("txnPanel").classList.remove("hidden");

  document.getElementById("txnTitle").innerText = id + " Details";
  document.getElementById("txnDate").innerText = t.date;
  document.getElementById("txnType").innerText = t.type;
  document.getElementById("txnSource").innerText = t.source;
  document.getElementById("txnRef").innerText = t.ref;
  document.getElementById("txnAmount").innerText = t.amount;
  document.getElementById("txnBalance").innerText = t.balance;
}

function closeTxn(){
  document.getElementById("txnPanel").classList.add("hidden");
}

/* EDIT MODAL */
function openEditModal(){
  const t = transactions[currentTxnId];

  document.getElementById("editModal").classList.remove("hidden");

  document.getElementById("editDate").value = t.date;
  document.getElementById("editType").value = t.type;
  document.getElementById("editSource").value = t.source;
  document.getElementById("editRef").value = t.ref;
  document.getElementById("editAmount").value = t.amount;
  document.getElementById("editBalance").value = t.balance;
}

function closeEditModal(){
  document.getElementById("editModal").classList.add("hidden");
}

function saveEdit(){

  const t = transactions[currentTxnId];

  t.date = document.getElementById("editDate").value;
  t.type = document.getElementById("editType").value;
  t.source = document.getElementById("editSource").value;
  t.ref = document.getElementById("editRef").value;
  t.amount = document.getElementById("editAmount").value;
  t.balance = document.getElementById("editBalance").value;

  selectTxn(currentTxnId);

  const rows = document.querySelectorAll("#txnBody tr");

  rows.forEach(row => {
    const id = row.querySelector(".link").dataset.id;

    if(id === currentTxnId){
      row.cells[1].innerText = t.date;
      row.cells[2].innerText = t.type;
      row.cells[3].innerText = t.source;
      row.cells[4].innerText = t.ref;
      row.cells[5].innerText = t.amount;
      row.cells[6].innerText = t.balance;
    }
  });

  closeEditModal();
}

/* SEARCH */
function searchTxn(){
  const input = document.getElementById("searchInput").value.toUpperCase();
  const rows = document.querySelectorAll("#txnBody tr");

  rows.forEach(row => {
    const id = row.querySelector(".link").innerText;
    row.style.display = id.includes(input) ? "" : "none";
  });
}

/* EXPORT CSV */
function exportCSV(){
  let csv = [];
  const rows = document.querySelectorAll("table tr");

  rows.forEach(row => {
    let cols = row.querySelectorAll("td, th");
    let data = [];

    cols.forEach(col => data.push(col.innerText));
    csv.push(data.join(","));
  });

  const blob = new Blob([csv.join("\n")], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "transactions.csv";
  a.click();
}