/* =========================
   ROW CLICK → DETAIL PANEL
========================= */
document.addEventListener("click", function(e) {
  const row = e.target.closest(".payment-row");
  if (!row || e.target.closest(".primary-btn") || e.target.closest(".close-btn")) return;

  const id = row.getAttribute("data-id");
  const date = row.getAttribute("data-date");
  const customer = row.getAttribute("data-customer");
  const builty = row.getAttribute("data-builty");
  const mode = row.getAttribute("data-mode");
  const reference = row.getAttribute("data-reference");
  const remarks = row.getAttribute("data-remarks");
  const amount = row.getAttribute("data-amount");

  selectPayment({ id, date, customer, builty, mode, reference, remarks, amount });
});


/* =========================
   OPEN DETAIL PANEL
========================= */
function selectPayment(p) {
  document.getElementById("paymentPanel").classList.remove("hidden");

  document.getElementById("payTitle").innerText = p.id + " Details";
  document.getElementById("payDate").innerText = p.date;
  document.getElementById("payCustomer").innerText = p.customer;
  document.getElementById("payBuilty").innerText = p.builty;
  document.getElementById("payMethod").innerText = p.mode;
  document.getElementById("payReference").innerText = p.reference ? p.reference : "—";
  document.getElementById("payRemarks").innerText = p.remarks ? p.remarks : "No remarks added.";
  document.getElementById("payAmount").innerText = parseFloat(p.amount).toLocaleString('en-IN'); 
}

/* =========================
   DATE FILTER TOGGLE LOGIC
========================= */
document.addEventListener("DOMContentLoaded", function() {
  const datePeriodSelect = document.getElementById("datePeriodSelect");
  const dateRangeBox = document.getElementById("dateRangeBox");
  const startDate = document.getElementById("startDate");
  const endDate = document.getElementById("endDate");

  if (datePeriodSelect && dateRangeBox) {
    datePeriodSelect.addEventListener("change", function() {
      if (this.value === "custom") {
        dateRangeBox.classList.remove("hidden");
        dateRangeBox.style.display = "flex"; // Inline row alignment ensure karne k liye
      } else {
        dateRangeBox.classList.add("hidden");
        dateRangeBox.style.display = "none";
        if (startDate) startDate.value = "";
        if (endDate) endDate.value = "";
      }
    });
  }
});


/* =========================
   CLOSE DETAIL PANEL
========================= */
function closePayment() {
  document.getElementById("paymentPanel").classList.add("hidden");
}


/* ==========================================
   GLOBAL MODAL CONTROLS (Accessible from HTML)
========================================== */
function openReceiptModal() {
  const modal = document.getElementById("receiptModal");
  if (modal) {
    modal.classList.remove("hidden");
    
    // Default date ko set karne ki logic yahan move kar di taake modal khulte hi date field populate ho
    const dateInput = document.getElementById("modalPaymentDate");
    if (dateInput && !dateInput.value) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }
  }
}

function closeReceiptModal() {
  const modal = document.getElementById("receiptModal");
  if (modal) {
    modal.classList.add("hidden");
    
    // 1. Main Form values reset (Inputs, textarea clear karega)
    const form = document.getElementById("paymentCreateForm");
    if (form) form.reset();
    
    // 2. Hidden field inputs reset
    document.getElementById("selectedBuiltyId").value = "";
    document.getElementById("selectedPaymentMode").value = "cash";
    
    // 3. Read-only Monetary Text labels reset (Left Side)
    document.getElementById("modalTotalFreight").innerText = "₹0";
    document.getElementById("modalAdvancePaid").innerText = "₹0";
    document.getElementById("modalOutstanding").innerText = "₹0";
    
    // 4. Live Financial Summary Text reset (Right Side)
    document.getElementById("sideCurrentBalance").innerText = "₹0";
    document.getElementById("sideRemainingText").innerText = "₹0";
    document.getElementById("sideRemainingText").style.color = "#475569"; // Default state color
    document.getElementById("sidePayingMainTotal").innerText = "₹0";
    
    // 5. Global tracker active outstanding variable variable ko reset karein
    activeOutstanding = 0;

    // 6. Payment Mode buttons classes reset (Cash active ho jaye baki inactive)
    const modeButtons = document.querySelectorAll("#paymentModeGroup .tag");
    modeButtons.forEach(b => b.classList.remove("active"));
    const cashBtn = document.querySelector('#paymentModeGroup .tag[data-mode="cash"]');
    if (cashBtn) cashBtn.classList.add("active");

    // 7. Reference box container ko hide karein
    const refBox = document.getElementById("referenceFieldBox");
    if (refBox) refBox.classList.add("hidden");

    // 8. Dropdown suggestions list hide aur clear
    const dropdownList = document.getElementById("builtyDropdownList");
    if (dropdownList) {
      dropdownList.classList.add("hidden");
      dropdownList.innerHTML = "";
    }
  }
}


/* ==========================================
   RECEIPT MODAL DYNAMIC INTERACTION LOGIC
========================================== */
const sampleBuilties = [
  { id: 1, builty_no: "B-88291", customer_name: "Global Logistics", total_freight: 12500, advance_paid: 5000, outstanding: 7500 },
  { id: 2, builty_no: "B-88285", customer_name: "Swift Transporters", total_freight: 25000, advance_paid: 15000, outstanding: 10000 },
  { id: 3, builty_no: "B-89001", customer_name: "Atlas Honda", total_freight: 50000, advance_paid: 0, outstanding: 50000 }
];

let activeOutstanding = 0;

document.addEventListener("DOMContentLoaded", function() {
  const builtyInput = document.getElementById("builtySearchInput");
  const dropdownList = document.getElementById("builtyDropdownList");
  const amountInput = document.getElementById("modalAmountInput");
  const modeButtons = document.querySelectorAll("#paymentModeGroup .tag");
  const refBox = document.getElementById("referenceFieldBox");
  const selectedModeInput = document.getElementById("selectedPaymentMode");

  /* 1. SEARCHABLE BUILTY DROPDOWN LOGIC */
  if (builtyInput && dropdownList) {
    builtyInput.addEventListener("input", function() {
      const value = this.value.toLowerCase().trim();
      dropdownList.innerHTML = "";

      if (!value) {
        dropdownList.classList.add("hidden");
        return;
      }

      const filtered = sampleBuilties.filter(b => b.builty_no.toLowerCase().includes(value));

      if (filtered.length > 0) {
        dropdownList.classList.remove("hidden");
        filtered.forEach(item => {
          const div = document.createElement("div");
          div.style.padding = "10px";
          div.style.cursor = "pointer";
          div.style.borderBottom = "1px solid #f1f5f9";
          div.innerText = `${item.builty_no} (${item.customer_name})`;
          
          div.addEventListener("mouseover", () => div.style.backgroundColor = "#f8fafc");
          div.addEventListener("mouseout", () => div.style.backgroundColor = "transparent");

          div.addEventListener("click", function() {
            builtyInput.value = item.builty_no;
            document.getElementById("selectedBuiltyId").value = item.id;
            document.getElementById("modalCustomerName").value = item.customer_name;
            
            document.getElementById("modalTotalFreight").innerText = "PKR " + item.total_freight.toLocaleString();
            document.getElementById("modalAdvancePaid").innerText = "PKR " + item.advance_paid.toLocaleString();
            document.getElementById("modalOutstanding").innerText = "PKR " + item.outstanding.toLocaleString();
            
            document.getElementById("sideCurrentBalance").innerText = "PKR " + item.outstanding.toLocaleString();
            activeOutstanding = item.outstanding;
            
            calculateLiveBalances();
            dropdownList.classList.add("hidden");
          });
          dropdownList.appendChild(div);
        });
      } else {
        dropdownList.classList.add("hidden");
      }
    });

    document.addEventListener("click", function(e) {
      if (!builtyInput.contains(e.target) && !dropdownList.contains(e.target)) {
        dropdownList.classList.add("hidden");
      }
    });
  }

  /* 2. LIVE FINANCIAL SUMMARY LOGIC */
  if (amountInput) {
    amountInput.addEventListener("input", function() {
      calculateLiveBalances();
    });
  }

  function calculateLiveBalances() {
  const payingAmount = parseFloat(document.getElementById("modalAmountInput").value) || 0;
  
  // 1. Main Amount (Save Payment button ke upar) -> Yahan input key-up live amount show hogi
  document.getElementById("sidePayingMainTotal").innerText = "PKR " + payingAmount.toLocaleString('en-IN');

  // 2. Remaining Logic Box calculation (Outstanding minus Paying Now)
  const remaining = activeOutstanding - payingAmount;
  
  if (remaining >= 0) {
    document.getElementById("sideRemainingText").innerText = "PKR " + remaining.toLocaleString('en-IN');
    document.getElementById("sideRemainingText").style.color = "#2563eb"; // Standard blue color
  } else {
    // Agar input outstanding se zyada ho jaye to advance status show ho jaye
    document.getElementById("sideRemainingText").innerText = "Advance: PKR " + Math.abs(remaining).toLocaleString('en-IN');
    document.getElementById("sideRemainingText").style.color = "#16a34a"; // Green color for advance/surplus
  }
}

  /* 3. CONDITIONAL PAYMENT MODE & REFERENCE BOX */
  modeButtons.forEach(btn => {
    btn.addEventListener("click", function() {
      modeButtons.forEach(b => b.classList.remove("active"));
      this.classList.add("active");

      const selectedMode = this.getAttribute("data-mode");
      selectedModeInput.value = selectedMode;

      if (selectedMode === "cash") {
        refBox.classList.add("hidden");
        document.getElementById("modalReferenceInput").value = "";
      } else {
        refBox.classList.remove("hidden");
        if (selectedMode === "cheque") {
          document.getElementById("referenceLabel").innerText = "Cheque No *";
        } else {
          document.getElementById("referenceLabel").innerText = "Transaction Reference No *";
        }
      }
    });
  });
});

function submitPaymentForm(addAnother) {
  const builtyId = document.getElementById("selectedBuiltyId").value;
  const amount = document.getElementById("modalAmountInput").value;
  
  if (!builtyId) {
    alert("Please select a valid Builty first.");
    return;
  }
  if (!amount || amount <= 0) {
    alert("Please enter a valid payment amount.");
    return;
  }

  console.log("Submitting form...", { addAnother: addAnother });
}



// prompt
// perfect ho gaya! chalo ab logic banaty han iski. aik or bat k ma postgres use kar raha is project ma to atomicity rakhni ha mujy or race conditions sy bhi bachna ha or bht zyada concurrent requests nhi hongi I know lekn pht bhi ma safe side chahta hon to logic robust, scalable or efficient hona chye Ok. isky iwala ye k payment kabhi bhi update or delete nhi hogi to agr tum chaho to CreateView bhi Use kar sakty lekn use CBV hi karna Ok. or jo dummy data hum js sy ly rahy han usko actual data k according rakh lo ab kyu k UI or JS blkul thik work kar rahi