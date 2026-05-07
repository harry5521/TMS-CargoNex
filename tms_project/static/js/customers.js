const customers = {
  "CUS-1024": {
    name: "Al-Farooq Logistics",
    phone: "+92 300 1234567",
    category: "Regular",
    builtiy: 142,
    balance: "Rs. 45,000",
    status: "Active"
  },
  "CUS-1025": {
    name: "Zubair Ahmed",
    phone: "+92 321 9876543",
    category: "Walk-in",
    builtiy: 3,
    balance: "Rs. 1,200",
    status: "Active"
  }
};

let currentCustomerId = null;

/* ROW CLICK */
document.addEventListener("click", function(e){
  const row = e.target.closest("tr");

  if (row) {
    const link = row.querySelector(".link");
    if (link) {
      selectCustomer(link.dataset.id);
    }
  }
});

/* OPEN PANEL */
function selectCustomer(id){
  const c = customers[id];
  if(!c) return;

  currentCustomerId = id;

  document.getElementById("customerPanel").classList.remove("hidden");

  document.getElementById("cTitle").innerText = id + " Details";
  document.getElementById("cName").innerText = c.name;
  document.getElementById("cPhone").innerText = c.phone;
  document.getElementById("cCategory").innerText = c.category;
  document.getElementById("cBuilty").innerText = c.builtiy;
  document.getElementById("cBalance").innerText = c.balance;
  document.getElementById("cStatus").innerText = c.status;
}

/* CLOSE PANEL */
function closeCustomer(){
  document.getElementById("customerPanel").classList.add("hidden");
}

/* OPEN MODAL */
function openEditModal(){
  const c = customers[currentCustomerId];

  document.getElementById("editModal").classList.remove("hidden");

  document.getElementById("editName").value = c.name;
  document.getElementById("editPhone").value = c.phone;
  document.getElementById("editCategory").value = c.category;
  document.getElementById("editBuilty").value = c.builtiy;
  document.getElementById("editBalance").value = c.balance;
  document.getElementById("editStatus").value = c.status;
}

/* CLOSE MODAL */
function closeEditModal(){
  document.getElementById("editModal").classList.add("hidden");
}

/* SAVE EDIT */
function saveEdit(){

  const c = customers[currentCustomerId];

  c.name = document.getElementById("editName").value;
  c.phone = document.getElementById("editPhone").value;
  c.category = document.getElementById("editCategory").value;
  c.builtiy = document.getElementById("editBuilty").value;
  c.balance = document.getElementById("editBalance").value;
  c.status = document.getElementById("editStatus").value;

  // Update panel
  selectCustomer(currentCustomerId);

  // Update table
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach(row => {
    const id = row.querySelector(".link").dataset.id;

    if(id === currentCustomerId){
      row.cells[1].innerText = c.name;
      row.cells[2].innerText = c.phone;
      row.cells[3].innerText = c.category;
      row.cells[4].innerText = c.builtiy;
      row.cells[5].innerText = c.balance;
      row.cells[6].innerText = c.status;
    }
  });

  closeEditModal();
}