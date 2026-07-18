/* =========================
   PAYMENT MODULE STATE
========================= */

let activeOutstanding = 0;
let activePaymentStatus = "";
let searchTimeout = null;
let searchController = null;


/* =========================
   HELPERS
========================= */

function getAmountInput() {
  return document.getElementById("modalAmountInput");
}

function getPaymentSubmitButtons() {
  return document.querySelectorAll(
    '#paymentCreateForm button[type="submit"]'
  );
}

function setPaymentSubmitDisabled(disabled) {
  getPaymentSubmitButtons().forEach(button => {
    button.disabled = disabled;
    button.style.opacity = disabled ? ".5" : "1";
    button.style.cursor = disabled ? "not-allowed" : "pointer";
  });
}

function showPaymentWarning(message) {
  const warning = document.getElementById("paymentWarning");

  if (!warning) return;

  warning.textContent = `⚠ ${message}`;
  warning.classList.remove("hidden");
}

function hidePaymentWarning() {
  const warning = document.getElementById("paymentWarning");

  if (!warning) return;

  warning.textContent = "";
  warning.classList.add("hidden");
}

function formatMoney(value) {
  return Number(value || 0).toLocaleString("en-PK", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  });
}


/* =========================
   LIVE BALANCE
========================= */

function calculateLiveBalances() {
  const amountInput = getAmountInput();
  const payingAmount = parseFloat(amountInput?.value) || 0;
  const remaining = activeOutstanding - payingAmount;

  document.getElementById("sidePayingMainTotal").innerText =
    `PKR ${formatMoney(payingAmount)}`;

  const remainingText = document.getElementById("sideRemainingText");

  if (remaining >= 0) {
    remainingText.innerText = `PKR ${formatMoney(remaining)}`;
    remainingText.style.color = "#2563eb";
  } else {
    remainingText.innerText =
      `Overpayment: PKR ${formatMoney(Math.abs(remaining))}`;

    remainingText.style.color = "#dc2626";
  }
}


/* =========================
   PAYMENT VALIDATION
========================= */

function updatePaymentValidation(showRequiredErrors = false) {

  const selectedBuiltyId =
    document.getElementById("selectedBuiltyId")?.value || "";

  const amountInput =
    document.getElementById("modalAmountInput");

  const amountValue =
    amountInput?.value.trim() || "";

  const amount =
    Number(amountValue);

  const paymentMode =
    document.getElementById("selectedPaymentMode")?.value || "cash";

  const referenceInput =
    document.getElementById("modalReferenceInput");

  const reference =
    referenceInput?.value.trim() || "";


  /*
   * Har validation run ke start par purani disabled
   * state clear karna zaroori hai.
   */
  if (amountInput) {
    amountInput.disabled = false;
  }

  setPaymentSubmitDisabled(false);
  hidePaymentWarning();


  /*
   * No Builty selected
   * Buttons enabled rahenge.
   * Form submit hone par warning show hogi.
   */
  if (!selectedBuiltyId) {

    if (showRequiredErrors) {
      showPaymentWarning(
        "Please select a valid Builty."
      );
    }

    return false;
  }


  /*
   * Fully paid Builty
   */
  if (
    activePaymentStatus === "paid" ||
    activeOutstanding <= 0
  ) {

    if (amountInput) {
      amountInput.value = "";
      amountInput.disabled = true;
    }

    calculateLiveBalances();

    showPaymentWarning(
      "This Builty has already been fully paid. No further payment can be recorded."
    );

    setPaymentSubmitDisabled(true);

    return false;
  }


  /*
   * Empty amount
   * Buttons enabled rahenge.
   * Submit par required warning show hogi.
   */
  if (amountValue === "") {

    if (showRequiredErrors) {
      showPaymentWarning(
        "Please enter the payment amount."
      );
    }

    return false;
  }


  /*
   * Invalid zero/negative amount
   */
  if (
    !Number.isFinite(amount) ||
    amount <= 0
  ) {

    showPaymentWarning(
      "Payment amount must be greater than zero."
    );

    setPaymentSubmitDisabled(true);

    return false;
  }


  /*
   * Overpayment
   */
  if (amount > activeOutstanding) {

    showPaymentWarning(
      "Payment amount cannot exceed the outstanding amount."
    );

    setPaymentSubmitDisabled(true);

    return false;
  }


  /*
   * Non-cash reference validation
   * Buttons disable nahi honge.
   * Submit par warning show hogi.
   */
  if (
    paymentMode !== "cash" &&
    !reference
  ) {

    if (showRequiredErrors) {

      showPaymentWarning(
        paymentMode === "cheque"
          ? "Cheque number is required."
          : "Transaction reference number is required."
      );

    }

    return false;
  }


  /*
   * Everything valid
   */
  hidePaymentWarning();
  setPaymentSubmitDisabled(false);

  return true;
}


/* =========================
   RESET SELECTED BUILTY
========================= */

function resetSelectedBuiltyState(keepSearchText = false) {
  const amountInput = getAmountInput();

  document.getElementById("selectedBuiltyId").value = "";
  document.getElementById("modalCustomerName").value = "";

  if (!keepSearchText) {
    document.getElementById("builtySearchInput").value = "";
  }

  document.getElementById("modalTotalFreight").innerText = "PKR 0";
  document.getElementById("modalAdvancePaid").innerText = "PKR 0";
  document.getElementById("modalOutstanding").innerText = "PKR 0";
  document.getElementById("sideCurrentBalance").innerText = "PKR 0";

  activeOutstanding = 0;
  activePaymentStatus = "";

  if (amountInput) {
    amountInput.value = "";
    amountInput.disabled = false;
  }

calculateLiveBalances();
hidePaymentWarning();
setPaymentSubmitDisabled(false);
}


/* =========================
   TABLE ROW → DETAIL PANEL
========================= */

document.addEventListener("click", function (event) {
  const row = event.target.closest(".payment-row");

  if (
    !row ||
    event.target.closest(".primary-btn") ||
    event.target.closest(".close-btn")
  ) {
    return;
  }

  selectPayment({
    id: row.dataset.id,
    date: row.dataset.date,
    customer: row.dataset.customer,
    builty: row.dataset.builty,
    mode: row.dataset.mode,
    reference: row.dataset.reference,
    remarks: row.dataset.remarks,
    amount: row.dataset.amount
  });
});

function selectPayment(payment) {
  document.getElementById("paymentPanel").classList.remove("hidden");

  document.getElementById("payTitle").innerText =
    `${payment.id} Details`;

  document.getElementById("payDate").innerText = payment.date;
  document.getElementById("payCustomer").innerText = payment.customer;
  document.getElementById("payBuilty").innerText = payment.builty;
  document.getElementById("payMethod").innerText = payment.mode;

  document.getElementById("payReference").innerText =
    payment.reference || "—";

  document.getElementById("payRemarks").innerText =
    payment.remarks || "No remarks added.";

  document.getElementById("payAmount").innerText =
    formatMoney(payment.amount);
}

function closePayment() {
  document.getElementById("paymentPanel").classList.add("hidden");
}


/* =========================
   MODAL CONTROLS
========================= */

function openReceiptModal() {

  const modal =
    document.getElementById("receiptModal");

  if (!modal) return;

  modal.classList.remove("hidden");

  const dateInput =
    document.getElementById("modalPaymentDate");

  if (dateInput && !dateInput.value) {

    const localDate = new Date();

    localDate.setMinutes(
      localDate.getMinutes() -
      localDate.getTimezoneOffset()
    );

    dateInput.value =
      localDate.toISOString().split("T")[0];
  }

  const selectedBuiltyId =
    document.getElementById(
      "selectedBuiltyId"
    )?.value;

  if (!selectedBuiltyId) {

    const amountInput =
      document.getElementById(
        "modalAmountInput"
      );

    if (amountInput) {
      amountInput.disabled = false;
    }

    hidePaymentWarning();
    setPaymentSubmitDisabled(false);

  } else {

    updatePaymentValidation(false);

  }
}

function closeReceiptModal() {
  const modal = document.getElementById("receiptModal");
  const form = document.getElementById("paymentCreateForm");

  if (!modal) return;

  modal.classList.add("hidden");

  if (searchController) {
    searchController.abort();
    searchController = null;
  }

  clearTimeout(searchTimeout);

  if (form) {
    form.reset();
  }

  document.getElementById("selectedPaymentMode").value = "cash";

  const modeButtons =
    document.querySelectorAll("#paymentModeGroup .tag");

  modeButtons.forEach(button =>
    button.classList.remove("active")
  );

  const cashButton =
    document.querySelector(
      '#paymentModeGroup .tag[data-mode="cash"]'
    );

  if (cashButton) {
    cashButton.classList.add("active");
  }

  const referenceBox =
    document.getElementById("referenceFieldBox");

  const referenceInput =
    document.getElementById("modalReferenceInput");

  if (referenceBox) {
    referenceBox.classList.add("hidden");
  }

  if (referenceInput) {
    referenceInput.required = false;
    referenceInput.value = "";
  }

  const dropdown =
    document.getElementById("builtyDropdownList");

  if (dropdown) {
    dropdown.innerHTML = "";
    dropdown.classList.add("hidden");
  }

  resetSelectedBuiltyState(false);
  const amountInput =
  document.getElementById("modalAmountInput");

if (amountInput) {
  amountInput.disabled = false;
}

hidePaymentWarning();
setPaymentSubmitDisabled(false);
}


/* =========================
   DOM READY
========================= */

document.addEventListener("DOMContentLoaded", function () {
  const builtyInput =
    document.getElementById("builtySearchInput");

  const dropdownList =
    document.getElementById("builtyDropdownList");

  const amountInput =
    document.getElementById("modalAmountInput");

  const paymentForm =
    document.getElementById("paymentCreateForm");

  const modeButtons =
    document.querySelectorAll("#paymentModeGroup .tag");

  const referenceBox =
    document.getElementById("referenceFieldBox");

  const referenceInput =
    document.getElementById("modalReferenceInput");

  const selectedModeInput =
    document.getElementById("selectedPaymentMode");


  /* DATE FILTER */

  const datePeriodSelect =
    document.getElementById("datePeriodSelect");

  const dateRangeBox =
    document.getElementById("dateRangeBox");

  const startDate =
    document.getElementById("startDate");

  const endDate =
    document.getElementById("endDate");

  if (datePeriodSelect && dateRangeBox) {
    datePeriodSelect.addEventListener("change", function () {
      const isCustom = this.value === "custom";

      dateRangeBox.classList.toggle("hidden", !isCustom);
      dateRangeBox.style.display = isCustom ? "flex" : "none";

      if (!isCustom) {
        if (startDate) startDate.value = "";
        if (endDate) endDate.value = "";
      }
    });
  }


  /* INITIAL STATE */

  setPaymentSubmitDisabled(false);


  /* BUILTY SEARCH */

  if (builtyInput && dropdownList) {
    builtyInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);

      const query = this.value.trim();

      /*
       User ne text change kiya hai, is liye pehle selected
       Builty ko invalidate karna zaroori hai.
      */
      resetSelectedBuiltyState(true);

      dropdownList.innerHTML = "";

      if (!query) {
        dropdownList.classList.add("hidden");

        if (searchController) {
          searchController.abort();
          searchController = null;
        }

        return;
      }

      searchTimeout = setTimeout(async function () {
        if (searchController) {
          searchController.abort();
        }

        searchController = new AbortController();

        try {
          const response = await fetch(
            `/tms/payments/search-builties/?q=${encodeURIComponent(query)}`,
            { signal: searchController.signal }
          );

          if (!response.ok) {
            throw new Error("Unable to search Builties.");
          }

          const builties = await response.json();

          /*
           Agar request ke response ke waqt input text change
           ho chuka ho to purana result render mat karo.
          */
          if (builtyInput.value.trim() !== query) {
            return;
          }

          dropdownList.innerHTML = "";

          if (!builties.length) {
            dropdownList.classList.add("hidden");
            return;
          }

          dropdownList.classList.remove("hidden");

          builties.forEach(item => {
            const option = document.createElement("div");
            const title = document.createElement("strong");
            const detail = document.createElement("small");

            option.style.padding = "10px";
            option.style.cursor = "pointer";
            option.style.borderBottom = "1px solid #f1f5f9";

            title.textContent = item.builty_no;

            const statusText =
              item.payment_status === "paid"
                ? " ✅ Paid"
                : item.payment_status === "partial"
                  ? " • Partial"
                  : " • To Pay";

            detail.textContent =
              `${item.customer_name}${statusText}`;

            option.appendChild(title);
            option.appendChild(document.createElement("br"));
            option.appendChild(detail);

            option.addEventListener("mouseenter", function () {
              option.style.background = "#f8fafc";
            });

            option.addEventListener("mouseleave", function () {
              option.style.background = "";
            });

            option.addEventListener("click", function () {
              builtyInput.value = item.builty_no;

              document.getElementById(
                "selectedBuiltyId"
              ).value = item.id;

              document.getElementById(
                "modalCustomerName"
              ).value = item.customer_name;

              document.getElementById(
                "modalTotalFreight"
              ).innerText =
                `PKR ${formatMoney(item.total_freight)}`;

              document.getElementById(
                "modalAdvancePaid"
              ).innerText =
                `PKR ${formatMoney(item.advance_paid)}`;

              document.getElementById(
                "modalOutstanding"
              ).innerText =
                `PKR ${formatMoney(item.outstanding)}`;

              document.getElementById(
                "sideCurrentBalance"
              ).innerText =
                `PKR ${formatMoney(item.outstanding)}`;

              activeOutstanding =
                Number(item.outstanding);

              activePaymentStatus =
                item.payment_status;

              dropdownList.classList.add("hidden");

              calculateLiveBalances();
              updatePaymentValidation(false);
            });

            dropdownList.appendChild(option);
          });

        } catch (error) {
          if (error.name !== "AbortError") {
            console.error(error);
            dropdownList.classList.add("hidden");
          }
        }
      }, 300);
    });

    document.addEventListener("click", function (event) {
      if (
        !builtyInput.contains(event.target) &&
        !dropdownList.contains(event.target)
      ) {
        dropdownList.classList.add("hidden");
      }
    });
  }


  /* AMOUNT VALIDATION */

  if (amountInput) {
    amountInput.addEventListener("input", function () {
      calculateLiveBalances();
      updatePaymentValidation(false);
    });
  }


  /* PAYMENT MODE */

  modeButtons.forEach(button => {
    button.addEventListener("click", function () {
      modeButtons.forEach(item =>
        item.classList.remove("active")
      );

      this.classList.add("active");

      const selectedMode = this.dataset.mode;
      selectedModeInput.value = selectedMode;

      if (selectedMode === "cash") {
        referenceBox.classList.add("hidden");
        referenceInput.value = "";
        referenceInput.required = false;
      } else {
        referenceBox.classList.remove("hidden");
        referenceInput.required = true;

        document.getElementById("referenceLabel").innerText =
          selectedMode === "cheque"
            ? "Cheque No *"
            : "Transaction Reference No *";
      }

      updatePaymentValidation(false);
    });
  });

  if (referenceInput) {
    referenceInput.addEventListener("input", function () {
      updatePaymentValidation(false);
    });
  }


  /* FINAL FORM VALIDATION */

  if (paymentForm) {
    paymentForm.addEventListener("submit", function (event) {
      if (!updatePaymentValidation(true)) {
        event.preventDefault();
      }
    });
  }


  /* SAVE & ADD ANOTHER */

  const params = new URLSearchParams(window.location.search);

  if (params.get("open_payment") === "1") {
    openReceiptModal();

    params.delete("open_payment");

    const newQuery = params.toString();
    const cleanUrl =
      window.location.pathname +
      (newQuery ? `?${newQuery}` : "");

    window.history.replaceState({}, "", cleanUrl);
  }
});