const builtiyData = {
  "LR-88291": {
    date: "24 May 2024",
    customer: "Global Exports",
    route: "Mumbai → Delhi",
    freight: "45000",
    advance: "15000",
    remaining: "30000",
    status: "Not Assigned"
  },
  "LR-88292": {
    date: "24 May 2024",
    customer: "Adani Logistics",
    route: "Ahmedabad → Chennai",
    freight: "62000",
    advance: "62000",
    remaining: "0",
    status: "In Transit"
  }
};

let currentBuiltyId = null;

/* ROW CLICK */
document.addEventListener("click", function (e) {

  const row = e.target.closest("tr");

  if (row && row.dataset.id) {
    selectBuilty(row.dataset.id);
  }

});

/* OPEN PANEL */
function selectBuilty(id) {
  const b = builtiyData[id];
  if(!b) return;

  currentBuiltyId = id;

  document.getElementById("builtyPanel").classList.remove("hidden");

  document.getElementById("builtyTitle").innerText = id + " Details";
  document.getElementById("bDate").innerText = b.date;
  document.getElementById("bCustomer").innerText = b.customer;
  document.getElementById("bRoute").innerText = b.route;
  document.getElementById("bFreight").innerText = b.freight;
  document.getElementById("bAdvance").innerText = b.advance;
  document.getElementById("bRemaining").innerText = b.remaining;
  document.getElementById("bStatus").innerText = b.status;
}

/* CLOSE PANEL */
function closeBuilty() {
  document.getElementById("builtyPanel").classList.add("hidden");
}

/* OPEN EDIT MODAL */
function openEditModal(){

  const b = builtiyData[currentBuiltyId];

  document.getElementById("editModal").classList.remove("hidden");

  document.getElementById("editDate").value = b.date;
  document.getElementById("editCustomer").value = b.customer;
  document.getElementById("editRoute").value = b.route;
  document.getElementById("editFreight").value = b.freight;
  document.getElementById("editAdvance").value = b.advance;
  document.getElementById("editRemaining").value = b.remaining;
  document.getElementById("editStatus").value = b.status;
}

/* CLOSE MODAL */
function closeEditModal(){
  document.getElementById("editModal").classList.add("hidden");
}

/* SAVE EDIT */
function saveEdit(){

  const b = builtiyData[currentBuiltyId];

  b.date = document.getElementById("editDate").value;
  b.customer = document.getElementById("editCustomer").value;
  b.route = document.getElementById("editRoute").value;
  b.freight = document.getElementById("editFreight").value;
  b.advance = document.getElementById("editAdvance").value;
  b.remaining = document.getElementById("editRemaining").value;
  b.status = document.getElementById("editStatus").value;

  // update panel
  selectBuilty(currentBuiltyId);

  // update table
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach(row => {
    const id = row.dataset.id;

    if(id === currentBuiltyId){
      row.cells[1].innerText = b.date;
      row.cells[2].innerText = b.customer;
      row.cells[3].innerText = b.route;
      row.cells[4].innerText = "₹" + b.freight;
      row.cells[5].innerText = "₹" + b.advance;
      row.cells[6].innerText = "₹" + b.remaining;
      row.cells[8].innerText = b.status;
    }
  });

  closeEditModal();
}