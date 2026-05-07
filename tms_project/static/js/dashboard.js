const builtiy = {
  "BL-8802": {
    customer: "Global Textiles",
    route: "Surat → Delhi",
    freight: "45,000",
    status: "Partial"
  },
  "BL-8801": {
    customer: "Reliance Retail",
    route: "Mumbai → Pune",
    freight: "12,500",
    status: "Paid"
  },
  "BL-8799": {
    customer: "Amazon Logistics",
    route: "Bangalore → Chennai",
    freight: "32,000",
    status: "Unpaid"
  }
};

let currentId = null;

/* OPEN PANEL */
function openDetail(id){
  const b = builtiy[id];
  if(!b) return;

  currentId = id;

  const panel = document.getElementById("detailPanel");
  panel.classList.remove("hidden");

  document.getElementById("detailTitle").innerText = id;
  document.getElementById("dCustomer").innerText = b.customer;
  document.getElementById("dRoute").innerText = b.route;
  document.getElementById("dFreight").innerText = b.freight;
  document.getElementById("dStatus").innerText = b.status;
}

/* CLOSE PANEL */
function closeDetail(){
  document.getElementById("detailPanel").classList.add("hidden");
}

/* OPEN EDIT MODAL */
function openEditModal(){
  const b = builtiy[currentId];

  document.getElementById("editModal").classList.remove("hidden");

  document.getElementById("editCustomer").value = b.customer;
  document.getElementById("editRoute").value = b.route;
  document.getElementById("editFreight").value = b.freight.replace("₹","").replace(",","");
  document.getElementById("editStatus").value = b.status;
}

/* CLOSE MODAL */
function closeEditModal(){
  document.getElementById("editModal").classList.add("hidden");
}

/* SAVE EDIT */
function saveEdit(){

  const b = builtiy[currentId];

  b.customer = document.getElementById("editCustomer").value;
  b.route = document.getElementById("editRoute").value;
  b.freight = document.getElementById("editFreight").value;
  b.status = document.getElementById("editStatus").value;

  // update panel
  openDetail(currentId);

  // update table
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach(row => {
    const id = row.querySelector(".link").innerText.trim();

    if(id === currentId){
      row.cells[1].innerText = b.customer;
      row.cells[2].innerText = b.route;
      row.cells[3].innerText = "₹" + b.freight;

      // status badge update
      row.cells[4].innerHTML = `<span class="badge">${b.status}</span>`;
    }
  });

  closeEditModal();
}

