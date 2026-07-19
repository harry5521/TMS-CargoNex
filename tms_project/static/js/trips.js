let activeTripDetailUrl = null;
let assignSearchTimer = null;


function formatMoney(value) {
  const number = Number(value || 0);
  return `PKR ${number.toLocaleString("en-PK", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}


function valueOrDash(value) {
  return value !== null && value !== undefined && String(value).trim() !== ""
    ? value
    : "—";
}


async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  });

  if (!response.ok) {
    throw new Error("Unable to load Trip information.");
  }

  return response.json();
}


function showModal(modal) {
  modal.classList.remove("hidden");
  requestAnimationFrame(function () {
    modal.classList.add("active");
  });
}


function hideModal(modal) {
  modal.classList.remove("active");
  setTimeout(function () {
    modal.classList.add("hidden");
  }, 220);
}


function showTripPanel() {

  const panel =
    document.getElementById("tripPanel");

  panel.classList.remove("hidden");

  requestAnimationFrame(function () {
    panel.classList.add("active");
  });

}

function closeTripPanel() {

  const panel =
    document.getElementById("tripPanel");

  panel.classList.remove("active");

  setTimeout(function () {

    panel.classList.add("hidden");
    activeTripDetailUrl = null;

  }, 260);

}

document.addEventListener("click", function (event) {
  const row = event.target.closest(".trip-row");

  if (!row || event.target.closest("button, form, a")) {
    return;
  }

  openTripPanel(row.dataset.detailUrl);
});


async function openTripPanel(detailUrl) {
  try {
    const data = await fetchJson(detailUrl);
    activeTripDetailUrl = detailUrl;

    document.getElementById("panelTripTitle").innerText = data.trip_no;
    document.getElementById("panelTripBuilty").innerText = data.builty.builty_no;
    document.getElementById("panelTripStatus").innerText = data.status_display;
    document.getElementById("panelScheduledDate").innerText = data.scheduled_date_display;
    document.getElementById("panelStartedAt").innerText = data.started_at_display;
    document.getElementById("panelCompletedAt").innerText = data.completed_at_display;
    document.getElementById("panelCustomer").innerText = data.builty.customer;
    document.getElementById("panelRoute").innerText = data.builty.route;
    document.getElementById("panelReceiver").innerText = data.builty.receiver_name;
    document.getElementById("panelVehicle").innerText = data.vehicle.registration_number;
    document.getElementById("panelDriver").innerText = data.driver.name;
    document.getElementById("panelDriverPhone").innerText = data.driver.phone;
    document.getElementById("panelFreight").innerText = formatMoney(data.builty.freight_amount);
    document.getElementById("panelOutstanding").innerText = formatMoney(data.builty.remaining_amount);
    document.getElementById("panelExpenses").innerText = formatMoney(data.total_expenses);

    const detailsBtn = document.getElementById("panelViewDetailsBtn");
    const expensesBtn = document.getElementById("panelManageExpensesBtn");
    const startForm = document.getElementById("panelStartForm");
    const completeForm = document.getElementById("panelCompleteForm");

    detailsBtn.onclick = function () {
      openTripDetailsModal(detailUrl);
    };

    expensesBtn.onclick = function () {
      openExpenseModal(detailUrl);
    };

    startForm.action = data.start_url;
    completeForm.action = data.complete_url;

    startForm.classList.toggle("hidden", !data.can_start);
    completeForm.classList.toggle("hidden", !data.can_complete);

    showTripPanel();
  } catch (error) {
    console.error(error);
    alert("Unable to load Trip details.");
  }
}


function openCurrentTripsModal() {
  showModal(document.getElementById("currentTripsModal"));
}


function closeCurrentTripsModal() {
  hideModal(document.getElementById("currentTripsModal"));
}


function openAssignTripModal() {

  const form =
    document.getElementById(
      "assignTripForm"
    );

  form.reset();

  document.getElementById(
    "assignBuiltyId"
  ).value = "";

  document.getElementById(
    "selectedBuiltyCard"
  ).classList.add("hidden");

  showAssignResultsPlaceholder(
    "Search for a finalized Builty. Results will appear here."
  );

  showModal(
    document.getElementById(
      "assignTripModal"
    )
  );

  setTimeout(function () {

    document.getElementById(
      "assignBuiltySearch"
    ).focus();

  }, 250);

}


function closeAssignTripModal() {
  hideModal(document.getElementById("assignTripModal"));
}

function showAssignResultsPlaceholder(message) {

  const placeholder =
    document.getElementById(
      "assignResultsPlaceholder"
    );

  const suggestions =
    document.getElementById(
      "assignBuiltySuggestions"
    );

  suggestions.innerHTML = "";
  suggestions.classList.add("hidden");

  placeholder.innerText = message;
  placeholder.classList.remove("hidden");

}


function showAssignSuggestions() {

  const placeholder =
    document.getElementById(
      "assignResultsPlaceholder"
    );

  const suggestions =
    document.getElementById(
      "assignBuiltySuggestions"
    );

  placeholder.classList.add("hidden");
  suggestions.classList.remove("hidden");

}

async function searchUnassignedBuilties(query) {

  const page =
    document.getElementById(
      "tripsPage"
    );

  const suggestions =
    document.getElementById(
      "assignBuiltySuggestions"
    );

  if (!query) {

    showAssignResultsPlaceholder(
      "Search for a finalized Builty. Results will appear here."
    );

    return;
  }

  showAssignResultsPlaceholder(
    "Searching finalized Builties..."
  );

  try {

    const url =
      `${page.dataset.unassignedSearchUrl}` +
      `?q=${encodeURIComponent(query)}`;

    const results =
      await fetchJson(url);

    suggestions.innerHTML = "";

    if (!results.length) {

      suggestions.innerHTML = `
        <div class="suggestion-empty">
          No finalized and unassigned Builty found.
        </div>
      `;

      showAssignSuggestions();
      return;
    }

    results.forEach(function (item) {

      const button =
        document.createElement("button");

      button.type = "button";
      button.className = "suggestion-item";

      button.innerHTML = `
        <strong>${item.builty_no}</strong>

        <span>
          ${item.customer} • ${item.route}
        </span>

        <small>
          ${item.vehicle} • ${item.driver}
        </small>
      `;

      button.addEventListener(
        "click",
        function () {

          document.getElementById(
            "assignBuiltyId"
          ).value = item.id;

          document.getElementById(
            "assignBuiltySearch"
          ).value = item.builty_no;

          document.getElementById(
            "selectedBuiltyNo"
          ).innerText = item.builty_no;

          document.getElementById(
            "selectedBuiltyCustomer"
          ).innerText = item.customer;

          document.getElementById(
            "selectedBuiltyRoute"
          ).innerText = item.route;

          document.getElementById(
            "selectedBuiltyAssignment"
          ).innerText =
            `${item.vehicle} • ${item.driver}`;

          document.getElementById(
            "selectedBuiltyCard"
          ).classList.remove("hidden");

          showAssignResultsPlaceholder(
            `${item.builty_no} selected. Press Assign Trip to continue.`
          );

        }
      );

      suggestions.appendChild(button);

    });

    showAssignSuggestions();

  } catch (error) {

    console.error(error);

    suggestions.innerHTML = `
      <div class="suggestion-empty">
        Unable to search Builties. Please try again.
      </div>
    `;

    showAssignSuggestions();

  }

}


async function openTripDetailsModal(detailUrl) {
  try {
    const data = await fetchJson(detailUrl);

    document.getElementById("detailsTripTitle").innerText = `${data.trip_no} Details`;
    document.getElementById("detailsBuiltyTitle").innerText = data.builty.builty_no;
    document.getElementById("detailCustomer").innerText = data.builty.customer;
    document.getElementById("detailCustomerPhone").innerText = valueOrDash(data.builty.customer_phone);
    document.getElementById("detailReceiver").innerText = data.builty.receiver_name;
    document.getElementById("detailReceiverPhone").innerText = valueOrDash(data.builty.receiver_phone);
    document.getElementById("detailRoute").innerText = data.builty.route;
    document.getElementById("detailGoods").innerText = data.builty.goods_description;
    document.getElementById("detailWeight").innerText = `${data.builty.weight} kg`;
    document.getElementById("detailPackages").innerText = valueOrDash(data.builty.package_count);
    document.getElementById("detailVehicle").innerText = `${data.vehicle.registration_number} • ${data.vehicle.type}`;
    document.getElementById("detailDriver").innerText = `${data.driver.name} (${data.driver.driver_code})`;
    document.getElementById("detailDriverPhone").innerText = data.driver.phone;
    document.getElementById("detailDriverLicense").innerText = data.driver.license_number;
    document.getElementById("detailFreight").innerText = formatMoney(data.builty.freight_amount);
    document.getElementById("detailAdvance").innerText = formatMoney(data.builty.advance_amount);
    document.getElementById("detailRemaining").innerText = formatMoney(data.builty.remaining_amount);
    document.getElementById("detailPaymentStatus").innerText = data.builty.payment_status;
    document.getElementById("detailNotes").innerText = valueOrDash(data.builty.notes);

    showModal(document.getElementById("tripDetailsModal"));
  } catch (error) {
    console.error(error);
    alert("Unable to load Builty details.");
  }
}


function closeTripDetailsModal() {
  hideModal(document.getElementById("tripDetailsModal"));
}


function createExpenseItem(expense, csrfToken) {
  const item = document.createElement("div");
  item.className = "expense-item";

  item.innerHTML = `
    <div class="expense-item-top">
      <div>
        <strong>${expense.title}</strong>
        <span>${expense.expense_no} • ${expense.expense_date_display}</span>
      </div>
      <strong>${formatMoney(expense.amount)}</strong>
    </div>
    <div class="expense-item-meta">
      <span>${expense.payment_mode_display}</span>
      <span>${expense.reference_no || "No reference"}</span>
    </div>
    <button type="button" class="edit-title-toggle">Edit Title</button>
    <form method="POST" action="${expense.update_title_url}" class="expense-title-form hidden">
      <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
      <input type="text" name="title" value="${expense.title}" required maxlength="200">
      <button type="submit">Save</button>
    </form>
  `;

  const toggle = item.querySelector(".edit-title-toggle");
  const form = item.querySelector(".expense-title-form");

  toggle.addEventListener("click", function () {
    form.classList.toggle("hidden");
  });

  return item;
}


async function openExpenseModal(detailUrl) {
  try {
    const data = await fetchJson(detailUrl);
    const form = document.getElementById("expenseCreateForm");
    const list = document.getElementById("expenseList");
    const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;

    form.action = data.expense_create_url;
    form.reset();
    document.getElementById("expenseDateInput").value = new Date().toISOString().slice(0, 10);
    document.getElementById("expenseTripTitle").innerText = `${data.trip_no} • ${data.builty.builty_no}`;
    document.getElementById("expenseTotal").innerText = formatMoney(data.total_expenses);

    list.innerHTML = "";

    if (!data.expenses.length) {
      list.innerHTML = '<div class="empty-modal-state">No expenses recorded for this Trip.</div>';
    } else {
      data.expenses.forEach(function (expense) {
        list.appendChild(createExpenseItem(expense, csrfToken));
      });
    }

    showModal(document.getElementById("expenseModal"));
  } catch (error) {
    console.error(error);
    alert("Unable to load Trip expenses.");
  }
}


function closeExpenseModal() {
  hideModal(document.getElementById("expenseModal"));
}


document.addEventListener("DOMContentLoaded", function () {
  const assignSearch = document.getElementById("assignBuiltySearch");
  const assignForm = document.getElementById("assignTripForm");
  const paymentMode = document.getElementById("expensePaymentMode");
  const reference = document.getElementById("expenseReferenceNo");

  assignSearch.addEventListener("input", function () {
    clearTimeout(assignSearchTimer);
    const query = this.value.trim();

    document.getElementById("assignBuiltyId").value = "";
    document.getElementById("selectedBuiltyCard").classList.add("hidden");

    assignSearchTimer = setTimeout(function () {
      searchUnassignedBuilties(query);
    }, 300);
  });

  assignForm.addEventListener("submit", function (event) {
    if (!document.getElementById("assignBuiltyId").value) {
      event.preventDefault();
      alert("Please select a finalized Builty.");
    }
  });

  paymentMode.addEventListener("change", function () {
    reference.required = this.value !== "cash";
  });

  const openExpenseId = document.getElementById("tripsPage").dataset.openExpensesId;
  if (openExpenseId) {
    const row = document.querySelector(`.trip-row[data-trip-id="${openExpenseId}"]`);
    if (row) {
      openExpenseModal(row.dataset.detailUrl);
    }
  }
});
