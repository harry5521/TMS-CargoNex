let activeBuiltyDetailUrl = null;
let activeBuiltyUpdateUrl = null;
let activeBuiltyCancelUrl = null;
let activeBuiltyNo = null;
let editingBuiltyId = null;

const autocompleteState = {};


/* =========================
   UTILITIES
========================= */

function valueOrDash(value) {
  return value !== null &&
    value !== undefined &&
    String(value).trim() !== ""
    ? String(value)
    : "—";
}

function formatMoney(value) {
  const number = Number(value || 0);

  return `PKR ${number.toLocaleString("en-PK", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })}`;
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  });

  if (!response.ok) {
    throw new Error("Unable to load Builty information.");
  }

  return response.json();
}

function localToday() {
  const date = new Date();
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().split("T")[0];
}

function showAnimatedElement(element) {
  if (!element) return;

  element.classList.remove("hidden");

  requestAnimationFrame(function () {
    element.classList.add("active");
  });
}

function hideAnimatedElement(element, duration = 250, callback = null) {
  if (!element) return;

  element.classList.remove("active");

  setTimeout(function () {
    element.classList.add("hidden");

    if (callback) callback();
  }, duration);
}

function showFormWarning(message) {
  const warning = document.getElementById("builtyFormWarning");
  warning.textContent = `⚠ ${message}`;
  warning.classList.remove("hidden");
}

function hideFormWarning() {
  const warning = document.getElementById("builtyFormWarning");
  warning.textContent = "";
  warning.classList.add("hidden");
}

function setFinancialFieldsLocked(locked) {

  const customerSearch =
    document.getElementById(
      "customerSearch"
    );

  const builtyDate =
    document.getElementById(
      "builtyDateInput"
    );

  const freight =
    document.getElementById(
      "totalFreight"
    );

  const advance =
    document.getElementById(
      "advanceAmount"
    );

  const notice =
    document.getElementById(
      "financialLockNotice"
    );

  const lockedDate =
    document.getElementById(
      "lockedBuiltyDate"
    );

  const lockedFreight =
    document.getElementById(
      "lockedFreightAmount"
    );

  const lockedAdvance =
    document.getElementById(
      "lockedAdvanceAmount"
    );

  customerSearch.disabled = locked;
  builtyDate.disabled = locked;
  freight.disabled = locked;
  advance.disabled = locked;

  lockedDate.value =
    builtyDate.value || "";

  lockedFreight.value =
    freight.value || "0";

  lockedAdvance.value =
    advance.value || "0";

  // Hidden mirror fields sirf finalized edit mein submit hon.
  lockedDate.disabled = !locked;
  lockedFreight.disabled = !locked;
  lockedAdvance.disabled = !locked;

  [
    customerSearch,
    builtyDate,
    freight,
    advance
  ].forEach(function (field) {

    field.classList.toggle(
      "financial-field-locked",
      locked
    );

    field.setAttribute(
      "aria-disabled",
      locked ? "true" : "false"
    );

  });

  notice.classList.toggle(
    "hidden",
    !locked
  );
}

function setFinancialFieldsLocked(locked) {
  const customerSearch = document.getElementById("customerSearch");
  const builtyDate = document.getElementById("builtyDateInput");
  const freight = document.getElementById("totalFreight");
  const advance = document.getElementById("advanceAmount");
  const notice = document.getElementById("financialLockNotice");

  customerSearch.readOnly = locked;
  builtyDate.readOnly = locked;
  freight.readOnly = locked;
  advance.readOnly = locked;

  [customerSearch, builtyDate, freight, advance].forEach(function (field) {
    field.classList.toggle("financial-field-locked", locked);
  });

  notice.classList.toggle("hidden", !locked);
}


/* =========================
   FILTER DATE RANGE
========================= */

function updateDateRangeVisibility() {
  const filter = document.getElementById("filterSelect");
  const box = document.getElementById("dateRangeBox");

  if (!filter || !box) return;

  box.classList.toggle("hidden", filter.value !== "range");
}


/* =========================
   RIGHT PANEL
========================= */

document.addEventListener("click", function (event) {
  const row = event.target.closest(".builty-row");

  if (
    !row ||
    event.target.closest(".action-btn") ||
    event.target.closest("button") ||
    event.target.closest("form")
  ) {
    return;
  }

  openBuiltyPanel(row);
});

async function openBuiltyPanel(row) {
  try {
    const data = await fetchJson(row.dataset.detailUrl);

    activeBuiltyDetailUrl = row.dataset.detailUrl;
    activeBuiltyUpdateUrl = row.dataset.updateUrl;
    activeBuiltyCancelUrl = row.dataset.cancelUrl;
    activeBuiltyNo = data.builty_no;

    document.getElementById("builtyTitle").innerText =
      `${data.builty_no} Details`;

    document.getElementById("builtyDocumentStatus").innerText =
      data.document_status_display;

    document.getElementById("bDate").innerText =
      data.builty_date_display;

    document.getElementById("bCustomer").innerText =
      valueOrDash(data.customer_name);

    document.getElementById("bPhone").innerText =
      valueOrDash(data.customer_phone);

    document.getElementById("bCnic").innerText =
      valueOrDash(data.customer_cnic);

    document.getElementById("bRoute").innerText =
      valueOrDash(data.route);

    document.getElementById("bReceiver").innerText =
      valueOrDash(data.receiver_name);

    document.getElementById("bReceiverPhone").innerText =
      valueOrDash(data.receiver_phone);

    document.getElementById("bGoods").innerText =
      valueOrDash(data.goods_description);

    document.getElementById("bWeight").innerText =
      Number(data.weight || 0) > 0
        ? `${data.weight}`
        : "—";

    document.getElementById("bPackages").innerText =
      valueOrDash(data.package_count);

    document.getElementById("bFreight").innerText =
      formatMoney(data.freight_amount);

    document.getElementById("bAdvance").innerText =
      formatMoney(data.advance_amount);

    document.getElementById("bRemaining").innerText =
      formatMoney(data.remaining_amount);

    document.getElementById("bPaymentStatus").innerText =
      data.payment_status_display;

    document.getElementById("bDispatchStatus").innerText =
      data.dispatch_status_display;

    document.getElementById("bVehicle").innerText =
      valueOrDash(data.vehicle_number);

    document.getElementById("bDriver").innerText =
      valueOrDash(data.driver_name);

    document.getElementById("bDriverPhone").innerText =
      valueOrDash(data.driver_phone);

    document.getElementById("bNotes").innerText =
      data.notes || "No notes added.";

    const cancelCard = document.getElementById("cancelReasonCard");
    cancelCard.classList.toggle(
      "hidden",
      data.document_status !== "cancelled"
    );

    document.getElementById("bCancelReason").innerText =
      valueOrDash(data.cancel_reason);

    const editButton = document.getElementById("panelEditBtn");
    const cancelButton = document.getElementById("panelCancelBtn");

    editButton.classList.toggle("hidden", !data.is_editable);
    cancelButton.classList.toggle(
      "hidden",
      data.document_status === "cancelled" ||
      data.dispatch_status !== "pending"
    );

    const layout = document.querySelector(".builty-layout");
    const panel = document.getElementById("builtyPanel");

    layout.classList.add("panel-open");
    panel.classList.remove("hidden");

    requestAnimationFrame(function () {
      panel.classList.add("active");
    });

  } catch (error) {
    console.error(error);
  }
}

function closeBuiltyPanel() {
  const layout = document.querySelector(".builty-layout");
  const panel = document.getElementById("builtyPanel");

  panel.classList.remove("active");

  setTimeout(function () {
    panel.classList.add("hidden");
    layout.classList.remove("panel-open");
  }, 280);
}

function editActiveBuilty() {
  if (!activeBuiltyDetailUrl || !activeBuiltyUpdateUrl) return;

  openBuiltyModalFromUrls(
    activeBuiltyDetailUrl,
    activeBuiltyUpdateUrl
  );
}

function cancelActiveBuilty(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  if (!activeBuiltyCancelUrl) return;

  openCancelModal(
    activeBuiltyCancelUrl,
    activeBuiltyNo || "this Builty"
  );
}


/* =========================
   FINANCE CALCULATION
========================= */

function calculateRemaining() {
  const freight = Number(
    document.getElementById("totalFreight").value || 0
  );

  const advance = Number(
    document.getElementById("advanceAmount").value || 0
  );

  const remaining = freight - advance;

  document.getElementById("remainingAmount").value =
    Math.max(remaining, 0).toFixed(2);

  const status = document.getElementById("paymentStatusPreview");

  if (freight > 0 && advance >= freight) {
    status.innerText = "Paid";
    status.className = "preview-paid";
  } else if (advance > 0) {
    status.innerText = "Partial";
    status.className = "preview-partial";
  } else {
    status.innerText = "To Pay";
    status.className = "preview-topay";
  }

  if (advance > freight) {
    showFormWarning(
      "Advance amount cannot be greater than total freight."
    );
  } else {
    hideFormWarning();
  }
}


/* =========================
   AUTOCOMPLETE
========================= */

function setupAutocomplete({
  key,
  searchInputId,
  hiddenInputId,
  suggestionsId,
  url,
  onSelect,
  onClear,
}) {
  const searchInput = document.getElementById(searchInputId);
  const hiddenInput = document.getElementById(hiddenInputId);
  const suggestions = document.getElementById(suggestionsId);

  autocompleteState[key] = {
    timer: null,
    controller: null,
  };

  searchInput.addEventListener("input", function () {
    if (this.readOnly) return;

    const state = autocompleteState[key];
    const query = this.value.trim();

    clearTimeout(state.timer);
    hiddenInput.value = "";

    if (onClear) onClear();

    suggestions.innerHTML = "";

    if (!query) {
      suggestions.classList.add("hidden");

      if (state.controller) {
        state.controller.abort();
        state.controller = null;
      }

      return;
    }

    state.timer = setTimeout(async function () {
      if (state.controller) {
        state.controller.abort();
      }

      state.controller = new AbortController();

      try {
        const params = new URLSearchParams({ q: query });

        if (editingBuiltyId) {
          params.set("builty_id", editingBuiltyId);
        }

        const response = await fetch(
          `${url}?${params.toString()}`,
          { signal: state.controller.signal }
        );

        if (!response.ok) {
          throw new Error("Search request failed.");
        }

        const results = await response.json();

        if (searchInput.value.trim() !== query) return;

        suggestions.innerHTML = "";

        if (!results.length) {
          suggestions.classList.add("hidden");
          return;
        }

        results.forEach(function (item) {
          const option = document.createElement("button");
          option.type = "button";
          option.className = "suggestion-item";

          const title = document.createElement("strong");
          title.textContent = item.label;

          const secondary = document.createElement("small");
          secondary.textContent = item.secondary || "";

          option.appendChild(title);
          option.appendChild(secondary);

          option.addEventListener("click", function () {
            hiddenInput.value = item.id;
            searchInput.value = item.label;
            suggestions.classList.add("hidden");
            suggestions.innerHTML = "";

            if (onSelect) onSelect(item);
          });

          suggestions.appendChild(option);
        });

        suggestions.classList.remove("hidden");

      } catch (error) {
        if (error.name !== "AbortError") {
          console.error(error);
        }
      }
    }, 300);
  });

  document.addEventListener("click", function (event) {
    if (
      !searchInput.contains(event.target) &&
      !suggestions.contains(event.target)
    ) {
      suggestions.classList.add("hidden");
    }
  });
}


/* =========================
   CREATE / EDIT MODAL
========================= */

function resetBuiltyForm() {
  editingBuiltyId = null;

  const form = document.getElementById("builtyForm");
  form.reset();
  form.action = form.dataset.createUrl;

  document.getElementById("customerId").value = "";
  document.getElementById("vehicleId").value = "";
  document.getElementById("driverId").value = "";

  document.getElementById("customerPhone").value = "";
  document.getElementById("customerCnic").value = "";

  document.getElementById("selectedVehicleText").innerText =
    "Not assigned";
  document.getElementById("selectedDriverText").innerText =
    "Not assigned";

  document.getElementById("builtyDateInput").value = localToday();
  document.getElementById("totalFreight").value = "0";
  document.getElementById("advanceAmount").value = "0";
  document.getElementById("remainingAmount").value = "0.00";

  document.getElementById("saveDraftBtn").classList.remove("hidden");
  document.getElementById("finalizeBuiltyBtn").innerText =
    "Finalize Builty";

  setFinancialFieldsLocked(false);

  hideFormWarning();
  calculateRemaining();
}

function openBuiltyModal(event = null, button = null) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  if (!button) {
    resetBuiltyForm();

    document.getElementById("builtyModalTitle").innerText =
      "Create Builty";
    document.getElementById("builtyModalSubtitle").innerText =
      "Save incomplete work as Draft or finalize it for dispatch.";

    showAnimatedElement(document.getElementById("builtyModal"));
    return;
  }

  const row = button.closest(".builty-row");
  if (!row) return;

  openBuiltyModalFromUrls(
    row.dataset.detailUrl,
    row.dataset.updateUrl
  );
}

async function openBuiltyModalFromUrls(detailUrl, updateUrl) {
  try {
    const data = await fetchJson(detailUrl);

    resetBuiltyForm();

    const form = document.getElementById("builtyForm");
    form.action = updateUrl;
    editingBuiltyId = data.id;

    document.getElementById("builtyModalTitle").innerText =
      `Edit ${data.builty_no}`;

    document.getElementById("builtyModalSubtitle").innerText =
      data.document_status === "draft"
        ? "Complete the Draft or finalize it for dispatch."
        : "Financial fields are locked. Only operational details can be updated before dispatch.";

    document.getElementById("customerId").value =
      data.customer_id;
    document.getElementById("customerSearch").value =
      data.customer_name;
    document.getElementById("customerPhone").value =
      data.customer_phone;
    document.getElementById("customerCnic").value =
      data.customer_cnic;

    document.getElementById("builtyDateInput").value =
      data.builty_date;
    document.getElementById("receiverNameInput").value =
      data.receiver_name;
    document.getElementById("receiverPhoneInput").value =
      data.receiver_phone;
    document.getElementById("originCityInput").value =
      data.origin_city;
    document.getElementById("destinationCityInput").value =
      data.destination_city;
    document.getElementById("goodsDescriptionInput").value =
      data.goods_description;
    document.getElementById("weightInput").value =
      data.weight;
    document.getElementById("packageCountInput").value =
      data.package_count;
    document.getElementById("totalFreight").value =
      data.freight_amount;
    document.getElementById("advanceAmount").value =
      data.advance_amount;

    document.getElementById("vehicleId").value =
      data.vehicle_id;
    document.getElementById("vehicleSearch").value =
      data.vehicle_label || data.vehicle_number;
    document.getElementById("selectedVehicleText").innerText =
      data.vehicle_number || "Not assigned";

    document.getElementById("driverId").value =
      data.driver_id;
    document.getElementById("driverSearch").value =
      data.driver_label || data.driver_name;
    document.getElementById("selectedDriverText").innerText =
      data.driver_name || "Not assigned";

    document.getElementById("notesInput").value =
      data.notes;

    const saveDraftButton = document.getElementById("saveDraftBtn");
    saveDraftButton.classList.toggle(
      "hidden",
      data.document_status === "finalized"
    );

    document.getElementById("finalizeBuiltyBtn").innerText =
      data.document_status === "finalized"
        ? "Update Builty"
        : "Finalize Builty";

    setFinancialFieldsLocked(
      data.financial_fields_editable === false
    );

    setFinancialFieldsLocked(
      data.financial_fields_editable === false
    );

    calculateRemaining();
    showAnimatedElement(document.getElementById("builtyModal"));

  } catch (error) {
    console.error(error);
  }
}

function closeBuiltyModal() {
  const modal = document.getElementById("builtyModal");

  hideAnimatedElement(modal, 250, function () {
    resetBuiltyForm();
  });
}

function validateFinalizeForm() {
  const requiredValues = [
    ["customerId", "Please select a valid customer."],
    ["receiverNameInput", "Receiver name is required."],
    ["originCityInput", "Origin city is required."],
    ["destinationCityInput", "Destination city is required."],
    ["goodsDescriptionInput", "Goods description is required."],
    ["vehicleId", "Vehicle assignment is required."],
    ["driverId", "Driver assignment is required."],
  ];

  for (const [id, message] of requiredValues) {
    const value = document.getElementById(id).value.trim();
    if (!value) {
      showFormWarning(message);
      return false;
    }
  }

  const weight = Number(
    document.getElementById("weightInput").value || 0
  );
  const freight = Number(
    document.getElementById("totalFreight").value || 0
  );
  const advance = Number(
    document.getElementById("advanceAmount").value || 0
  );

  if (weight <= 0) {
    showFormWarning("Weight must be greater than zero.");
    return false;
  }

  if (freight <= 0) {
    showFormWarning("Freight amount must be greater than zero.");
    return false;
  }

  if (advance < 0 || advance > freight) {
    showFormWarning(
      "Advance amount must be between zero and total freight."
    );
    return false;
  }

  const origin = document
    .getElementById("originCityInput")
    .value.trim()
    .toLowerCase();

  const destination = document
    .getElementById("destinationCityInput")
    .value.trim()
    .toLowerCase();

  if (origin === destination) {
    showFormWarning("Origin and destination cannot be the same.");
    return false;
  }

  hideFormWarning();
  return true;
}


/* =========================
   CANCEL MODAL
========================= */

function openCancelBuiltyConfirm(event, button) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  if (!button || typeof button.closest !== "function") return;

  const row = button.closest(".builty-row");
  if (!row) return;

  openCancelModal(
    row.dataset.cancelUrl,
    row.dataset.builtyNo
  );
}

function openCancelModal(cancelUrl, builtyNo) {
  const form = document.getElementById("cancelBuiltyForm");
  form.action = cancelUrl;

  document.getElementById("cancelBuiltyName").innerText =
    builtyNo || "this Builty";

  document.getElementById("cancelReasonInput").value = "";

  const button = document.getElementById("confirmCancelBtn");
  button.disabled = false;
  button.innerText = "Yes, Cancel";

  showAnimatedElement(document.getElementById("cancelBuiltyModal"));
}

function closeCancelBuiltyConfirm() {
  hideAnimatedElement(
    document.getElementById("cancelBuiltyModal"),
    220,
    function () {
      document.getElementById("cancelReasonInput").value = "";
    }
  );
}


/* =========================
   INITIALIZATION
========================= */

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("builtyForm");

  setupAutocomplete({
    key: "customer",
    searchInputId: "customerSearch",
    hiddenInputId: "customerId",
    suggestionsId: "customerSuggestions",
    url: form.dataset.customerSearchUrl,
    onSelect: function (item) {
      document.getElementById("customerPhone").value =
        item.phone || "";
      document.getElementById("customerCnic").value =
        item.cnic || "";
    },
    onClear: function () {
      document.getElementById("customerPhone").value = "";
      document.getElementById("customerCnic").value = "";
    },
  });

  setupAutocomplete({
    key: "vehicle",
    searchInputId: "vehicleSearch",
    hiddenInputId: "vehicleId",
    suggestionsId: "vehicleSuggestions",
    url: form.dataset.vehicleSearchUrl,
    onSelect: function (item) {
      document.getElementById("selectedVehicleText").innerText =
        item.registration_number || item.label;
    },
    onClear: function () {
      document.getElementById("selectedVehicleText").innerText =
        "Not assigned";
    },
  });

  setupAutocomplete({
    key: "driver",
    searchInputId: "driverSearch",
    hiddenInputId: "driverId",
    suggestionsId: "driverSuggestions",
    url: form.dataset.driverSearchUrl,
    onSelect: function (item) {
      document.getElementById("selectedDriverText").innerText =
        `${item.full_name || item.label}${item.phone ? ` • ${item.phone}` : ""}`;
    },
    onClear: function () {
      document.getElementById("selectedDriverText").innerText =
        "Not assigned";
    },
  });

  document
    .getElementById("totalFreight")
    .addEventListener("input", calculateRemaining);

  document
    .getElementById("advanceAmount")
    .addEventListener("input", calculateRemaining);

  document
    .getElementById("filterSelect")
    .addEventListener("change", updateDateRangeVisibility);

  form.addEventListener(
  "submit",
  function (event) {

    const submitter =
      event.submitter;

    const action =
      submitter?.dataset.action
      || "finalize";

    // Button disable karne se pehle action
    // hidden input mein save karna zaroori hai.
    document.getElementById(
      "submitActionInput"
    ).value = action;

    if (
      !document.getElementById(
        "customerId"
      ).value
    ) {

      event.preventDefault();

      showFormWarning(
        "Please select a valid customer."
      );

      return;
    }

    if (
      action === "finalize"
      && !validateFinalizeForm()
    ) {

      event.preventDefault();
      return;
    }

    if (submitter) {

      submitter.disabled = true;

      submitter.innerText =
        action === "draft"
          ? "Saving Draft..."
          : "Saving...";

    }

  }
);

  document
    .getElementById("cancelBuiltyForm")
    .addEventListener("submit", function (event) {
      const reason = document
        .getElementById("cancelReasonInput")
        .value.trim();

      if (!reason) {
        event.preventDefault();
        return;
      }

      const button = document.getElementById("confirmCancelBtn");
      button.disabled = true;
      button.innerText = "Cancelling...";
    });

  updateDateRangeVisibility();
  resetBuiltyForm();

  const params = new URLSearchParams(window.location.search);
  if (params.get("open_builty") === "1") {
    openBuiltyModal();
  }
});
