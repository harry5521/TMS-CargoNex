const trips = {
  "TRP-001": {
    driver: "Ali Khan",
    vehicle: "ABC-123",
    status: "In Transit",
    route: "Karachi → Lahore",
    freight: 3500,
    expenses: 500
  },
  "TRP-002": {
    driver: "Ahmed Raza",
    vehicle: "XYZ-456",
    status: "Pending",
    route: "Islamabad → Multan",
    freight: 2800,
    expenses: 300
  }
};

let currentTripId = null;

// Select Trip
function selectTrip(id, el) {
  const trip = trips[id];
  if(!trip) return;

  currentTripId = id;

  // ✅ REMOVE OLD ACTIVE ROW
  document.querySelectorAll("tbody tr").forEach(r => {
    r.classList.remove("active-row");
  });

  // ✅ ADD ACTIVE TO CLICKED ROW
  if (el) {
    el.classList.add("active-row");
  }

  // PANEL OPEN
  document.getElementById("tripPanel").classList.remove("hidden");
  document.querySelector(".trips-layout").classList.add("active");

  // DATA FILL
  document.getElementById("tripTitle").innerText = id + " Details";
  document.getElementById("status").innerText = trip.status;
  document.getElementById("driver").innerText = trip.driver;
  document.getElementById("vehicle").innerText = trip.vehicle;
  document.getElementById("route").innerText = trip.route;
  document.getElementById("freight").innerText = trip.freight;
  document.getElementById("expenses").innerText = trip.expenses;
  document.getElementById("profit").innerText = trip.freight - trip.expenses;
}

/* CLOSE PANEL */
function closePanel() {
  document.getElementById("tripPanel").classList.add("hidden");
  document.querySelector(".trips-layout").classList.remove("active");

  // ✅ REMOVE ACTIVE ROW
  document.querySelectorAll("tbody tr").forEach(r => {
    r.classList.remove("active-row");
  });
}

/* OPEN EDIT MODAL */
function openEditModal(){
  const t = trips[currentTripId];

  document.getElementById("editModal").classList.remove("hidden");

  document.getElementById("editDriver").value = t.driver;
  document.getElementById("editVehicle").value = t.vehicle;
  document.getElementById("editRoute").value = t.route;
  document.getElementById("editStatus").value = t.status;
  document.getElementById("editFreight").value = t.freight;
  document.getElementById("editExpenses").value = t.expenses;
}

/* CLOSE MODAL */
function closeEditModal(){
  document.getElementById("editModal").classList.add("hidden");
}

/* SAVE EDIT */
function saveEdit(){

  const t = trips[currentTripId];

  t.driver = document.getElementById("editDriver").value;
  t.vehicle = document.getElementById("editVehicle").value;
  t.route = document.getElementById("editRoute").value;
  t.status = document.getElementById("editStatus").value;
  t.freight = Number(document.getElementById("editFreight").value);
  t.expenses = Number(document.getElementById("editExpenses").value);

  // Update panel
  selectTrip(currentTripId);

  // Update table
  const rows = document.querySelectorAll("tbody tr");

  rows.forEach(row => {
    const id = row.querySelector(".link").innerText.trim();

    if(id === currentTripId){
      row.cells[2].innerText = t.route;
      row.cells[3].innerText = t.vehicle;

      const badge = row.cells[4].querySelector(".badge");
      badge.innerText = t.status;

      badge.className = "badge " + (
        t.status === "In Transit" ? "in-transit" : "pending"
      );
    }
  });

  closeEditModal();
}


/* EXPENSE STORAGE */
let tripExpenses = {};

/* OPEN MODAL */
function openExpenseModal(){
  document.getElementById("expenseModal").classList.remove("hidden");
  renderExpenses();
}

/* CLOSE MODAL */
function closeExpenseModal(){
  document.getElementById("expenseModal").classList.add("hidden");
}

/* ADD EXPENSE */
function addExpense(){
  const type = document.getElementById("expType").value;
  const amount = document.getElementById("expAmount").value;
  const date = document.getElementById("expDate").value;
  const note = document.getElementById("expNote").value;

  if(!amount) return alert("Enter amount");

  if(!tripExpenses[currentTripId]){
    tripExpenses[currentTripId] = [];
  }

  tripExpenses[currentTripId].push({type, amount, date, note});

  renderExpenses();

  document.getElementById("expAmount").value = "";
  document.getElementById("expNote").value = "";
}

/* RENDER */
function renderExpenses(){
  const list = document.getElementById("expenseList");
  list.innerHTML = "";

  const data = tripExpenses[currentTripId] || [];

  data.forEach(e => {
    list.innerHTML += `
      <tr>
        <td>${e.type}</td>
        <td>Rs. ${e.amount}</td>
        <td>${e.date}</td>
        <td>${e.note || "-"}</td>
      </tr>
    `;
  });
}