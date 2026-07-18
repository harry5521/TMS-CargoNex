let activeVehicleDepreciationUrl = null;
let selectedVehicleDeleteForm = null;
let vehicleDeleteSubmitting = false;


/* =========================
   UTILITIES
========================= */

function valueOrDash(value) {
  return value !== null &&
         value !== undefined &&
         String(value).trim() !== ""
    ? value
    : "—";
}


function formatMoney(value) {

  const number = Number(value || 0);

  return `PKR ${number.toLocaleString("en-PK", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })}`;
}


async function fetchJson(url) {

  const response = await fetch(url, {
    headers: {
      "X-Requested-With": "XMLHttpRequest"
    }
  });

  if (!response.ok) {
    throw new Error(
      "Unable to load vehicle information."
    );
  }

  return response.json();
}


/* =========================
   RIGHT PANEL ANIMATION
========================= */

function showVehiclePanelSmooth() {

  const layout =
    document.querySelector(".vehicles-layout");

  const panel =
    document.getElementById("vehiclePanel");

  layout.classList.add("panel-open");
  panel.classList.remove("hidden");

  requestAnimationFrame(function () {
    panel.classList.add("active");
  });
}


function closeVehiclePanel() {

  const layout =
    document.querySelector(".vehicles-layout");

  const panel =
    document.getElementById("vehiclePanel");

  panel.classList.remove("active");

  setTimeout(function () {

    panel.classList.add("hidden");
    layout.classList.remove("panel-open");
    activeVehicleDepreciationUrl = null;

  }, 280);
}


/* =========================
   MODAL ANIMATION HELPERS
========================= */

function showAnimatedModal(modal) {

  modal.classList.remove("hidden");

  requestAnimationFrame(function () {
    modal.classList.add("active");
  });
}


function hideAnimatedModal(
  modal,
  duration,
  callback = null
) {

  modal.classList.remove("active");

  setTimeout(function () {

    modal.classList.add("hidden");

    if (callback) {
      callback();
    }

  }, duration);
}


/* =========================
   VEHICLE RIGHT PANEL
========================= */

document.addEventListener("click", function (event) {

  const row =
    event.target.closest(".vehicle-row");

  if (
    !row ||
    event.target.closest(".action-btn") ||
    event.target.closest("form")
  ) {
    return;
  }

  openVehiclePanel(row);
});


async function openVehiclePanel(row) {

  try {

    const data =
      await fetchJson(row.dataset.detailUrl);

    activeVehicleDepreciationUrl =
      row.dataset.depreciationUrl;

    document.getElementById(
      "panelVehicleTitle"
    ).innerText = data.registration_number;

    document.getElementById(
      "panelVehicleCode"
    ).innerText = data.vehicle_code;

    document.getElementById(
      "panelRegistration"
    ).innerText = data.registration_number;

    document.getElementById(
      "panelVehicleType"
    ).innerText = data.vehicle_type_display;

    document.getElementById(
      "panelBodyType"
    ).innerText = data.body_type_display;

    document.getElementById(
      "panelMakeModel"
    ).innerText = valueOrDash(
      `${data.make || ""} ${data.model || ""}`.trim()
    );

    document.getElementById(
      "panelModelYear"
    ).innerText = valueOrDash(data.model_year);

    document.getElementById(
      "panelCapacity"
    ).innerText = data.capacity_tons
      ? `${data.capacity_tons} Tons`
      : "—";

    document.getElementById(
      "panelChassis"
    ).innerText = valueOrDash(
      data.chassis_number
    );

    document.getElementById(
      "panelEngine"
    ).innerText = valueOrDash(
      data.engine_number
    );

    document.getElementById(
      "panelColor"
    ).innerText = valueOrDash(
      data.color
    );

    document.getElementById(
      "panelOwnership"
    ).innerText = data.ownership_type_display;

    document.getElementById(
      "panelOwnerName"
    ).innerText = valueOrDash(
      data.owner_name
    );

    document.getElementById(
      "panelOwnerPhone"
    ).innerText = valueOrDash(
      data.owner_phone
    );

    document.getElementById(
      "panelPurchaseCost"
    ).innerText = data.purchase_cost
      ? formatMoney(data.purchase_cost)
      : "Not Applicable";

    document.getElementById(
      "panelBookValue"
    ).innerText = data.current_book_value
      ? formatMoney(data.current_book_value)
      : "Not Applicable";

    document.getElementById(
      "panelVehicleStatus"
    ).innerText = data.status_display;

    document.getElementById(
      "panelVehicleNotes"
    ).innerText = data.notes
      ? data.notes
      : "No notes added.";

    const depreciationButton =
      document.getElementById(
        "viewDepreciationBtn"
      );

    depreciationButton.innerText =
      data.depreciation_applicable
        ? "View Depreciation"
        : "Depreciation Not Applicable";

    showVehiclePanelSmooth();

  } catch (error) {

    console.error(error);
    alert("Unable to load vehicle details.");

  }
}


/* =========================
   OWNERSHIP / STATUS FIELDS
========================= */

function updateOwnershipFields() {

  const ownership =
    document.getElementById(
      "ownershipTypeInput"
    ).value;

  const ownerFields =
    document.getElementById("ownerFields");

  const depreciationFields =
    document.getElementById(
      "depreciationFields"
    );

  const ownerName =
    document.getElementById(
      "ownerNameInput"
    );

  const purchaseDate =
    document.getElementById(
      "purchaseDateInput"
    );

  const purchaseCost =
    document.getElementById(
      "purchaseCostInput"
    );

  const depreciationStart =
    document.getElementById(
      "depreciationStartInput"
    );

  const usefulLife =
    document.getElementById(
      "usefulLifeInput"
    );

  const companyOwned =
    ownership === "company_owned";

  ownerFields.classList.toggle(
    "hidden",
    companyOwned
  );

  depreciationFields.classList.toggle(
    "hidden",
    !companyOwned
  );

  ownerName.required = !companyOwned;
  purchaseDate.required = companyOwned;
  purchaseCost.required = companyOwned;
  depreciationStart.required = companyOwned;
  usefulLife.required = companyOwned;
}


function updateDisposalFields() {

  const status =
    document.getElementById(
      "vehicleStatusInput"
    ).value;

  const disposalFields =
    document.getElementById(
      "disposalFields"
    );

  const disposalDate =
    document.getElementById(
      "disposalDateInput"
    );

  const disposalAmount =
    document.getElementById(
      "disposalAmountInput"
    );

  const isSold = status === "sold";

  disposalFields.classList.toggle(
    "hidden",
    !isSold
  );

  disposalDate.required = isSold;
  disposalAmount.required = isSold;
}


/* =========================
   CREATE / EDIT MODAL
========================= */

function resetVehicleFormDefaults() {

  const form =
    document.getElementById("vehicleForm");

  form.reset();

  document.getElementById(
    "ownershipTypeInput"
  ).value = "company_owned";

  document.getElementById(
    "vehicleStatusInput"
  ).value = "available";

  document.getElementById(
    "usefulLifeInput"
  ).value = "10";

  document.getElementById(
    "residualValueInput"
  ).value = "0";

  updateOwnershipFields();
  updateDisposalFields();
}


async function openVehicleModal(
  event = null,
  button = null
) {

  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const modal =
    document.getElementById("vehicleModal");

  const form =
    document.getElementById("vehicleForm");

  const title =
    document.getElementById(
      "vehicleModalTitle"
    );

  const submitButton =
    document.getElementById(
      "vehicleSubmitBtn"
    );

  resetVehicleFormDefaults();

  if (!button) {

    title.innerText = "Add Vehicle";
    submitButton.innerText = "Save Vehicle";
    form.action = form.dataset.createUrl;

    showAnimatedModal(modal);
    return;
  }

  const row =
    button.closest(".vehicle-row");

  if (!row) {
    return;
  }

  try {

    const data =
      await fetchJson(row.dataset.detailUrl);

    title.innerText = "Edit Vehicle";
    submitButton.innerText = "Update Vehicle";
    form.action = row.dataset.updateUrl;

    document.getElementById(
      "registrationInput"
    ).value = data.registration_number || "";

    document.getElementById(
      "vehicleTypeInput"
    ).value = data.vehicle_type || "truck";

    document.getElementById(
      "bodyTypeInput"
    ).value = data.body_type || "open";

    document.getElementById(
      "makeInput"
    ).value = data.make || "";

    document.getElementById(
      "modelInput"
    ).value = data.model || "";

    document.getElementById(
      "modelYearInput"
    ).value = data.model_year || "";

    document.getElementById(
      "colorInput"
    ).value = data.color || "";

    document.getElementById(
      "chassisInput"
    ).value = data.chassis_number || "";

    document.getElementById(
      "engineInput"
    ).value = data.engine_number || "";

    document.getElementById(
      "capacityInput"
    ).value = data.capacity_tons || "";

    document.getElementById(
      "ownershipTypeInput"
    ).value = data.ownership_type;

    document.getElementById(
      "ownerNameInput"
    ).value = data.owner_name || "";

    document.getElementById(
      "ownerPhoneInput"
    ).value = data.owner_phone || "";

    document.getElementById(
      "purchaseDateInput"
    ).value = data.purchase_date || "";

    document.getElementById(
      "purchaseCostInput"
    ).value = data.purchase_cost || "";

    document.getElementById(
      "depreciationStartInput"
    ).value =
      data.depreciation_start_date || "";

    document.getElementById(
      "residualValueInput"
    ).value = data.residual_value || "0";

    document.getElementById(
      "usefulLifeInput"
    ).value =
      data.useful_life_years || "10";

    document.getElementById(
      "vehicleStatusInput"
    ).value = data.status || "available";

    document.getElementById(
      "disposalDateInput"
    ).value = data.disposal_date || "";

    document.getElementById(
      "disposalAmountInput"
    ).value = data.disposal_amount || "";

    document.getElementById(
      "vehicleNotesInput"
    ).value = data.notes || "";

    updateOwnershipFields();
    updateDisposalFields();

    showAnimatedModal(modal);

  } catch (error) {

    console.error(error);
    alert("Unable to load vehicle for editing.");

  }
}


function closeVehicleModal() {

  const modal =
    document.getElementById("vehicleModal");

  const form =
    document.getElementById("vehicleForm");

  hideAnimatedModal(
    modal,
    250,
    function () {

      resetVehicleFormDefaults();
      form.action = form.dataset.createUrl;

      const submitButton =
        document.getElementById(
          "vehicleSubmitBtn"
        );

      submitButton.disabled = false;
      submitButton.innerText = "Save Vehicle";

    }
  );
}


/* =========================
   DEPRECIATION MODAL
========================= */

async function openDepreciationModal() {

  if (!activeVehicleDepreciationUrl) {
    return;
  }

  const modal =
    document.getElementById(
      "depreciationModal"
    );

  const content =
    document.getElementById(
      "depreciationContent"
    );

  const warning =
    document.getElementById(
      "depreciationNotApplicable"
    );

  try {

    const data =
      await fetchJson(
        activeVehicleDepreciationUrl
      );

    document.getElementById(
      "depreciationVehicleTitle"
    ).innerText =
      `${data.vehicle_code} • ${data.registration_number}`;

    if (!data.applicable) {

      content.classList.add("hidden");

      warning.innerText =
        data.message ||
        "Depreciation is not applicable.";

      warning.classList.remove("hidden");

      showAnimatedModal(modal);
      return;
    }

    warning.classList.add("hidden");
    content.classList.remove("hidden");

    document.getElementById(
      "depPurchaseCost"
    ).innerText = formatMoney(
      data.purchase_cost
    );

    document.getElementById(
      "depBookValue"
    ).innerText = formatMoney(
      data.current_book_value
    );

    document.getElementById(
      "depAccumulated"
    ).innerText = formatMoney(
      data.accumulated_depreciation
    );

    document.getElementById(
      "depResidual"
    ).innerText = formatMoney(
      data.residual_value
    );

    document.getElementById(
      "depDepreciable"
    ).innerText = formatMoney(
      data.depreciable_amount
    );

    document.getElementById(
      "depUsefulLife"
    ).innerText =
      `${data.useful_life_years} Years`;

    document.getElementById(
      "depAnnual"
    ).innerText = formatMoney(
      data.annual_depreciation
    );

    document.getElementById(
      "depMonthly"
    ).innerText = formatMoney(
      data.monthly_depreciation
    );

    document.getElementById(
      "depElapsed"
    ).innerText =
      `${data.elapsed_months} Months`;

    document.getElementById(
      "depRemaining"
    ).innerText =
      `${data.remaining_months} Months`;

    document.getElementById(
      "depAsOf"
    ).innerText =
      data.as_of_date_display;

    const percent = Math.min(
      Number(data.depreciation_percent || 0),
      100
    );

    document.getElementById(
      "depPercent"
    ).innerText = `${percent.toFixed(2)}%`;

    document.getElementById(
      "depProgressFill"
    ).style.width = `${percent}%`;

    showAnimatedModal(modal);

  } catch (error) {

    console.error(error);
    alert("Unable to calculate depreciation.");

  }
}


function closeDepreciationModal() {

  const modal =
    document.getElementById(
      "depreciationModal"
    );

  hideAnimatedModal(
    modal,
    250
  );
}


/* =========================
   DELETE CONFIRMATION
========================= */

function openVehicleDeleteConfirm(
  event,
  button
) {

  event.preventDefault();
  event.stopPropagation();

  if (
    !button ||
    typeof button.closest !== "function"
  ) {
    return;
  }

  selectedVehicleDeleteForm =
    button.closest(
      ".vehicle-delete-form"
    );

  const row =
    button.closest(".vehicle-row");

  const registration =
    row?.querySelector(
      "td:nth-child(2)"
    )?.innerText.trim() || "this vehicle";

  document.getElementById(
    "deleteVehicleName"
  ).innerText = registration;

  vehicleDeleteSubmitting = false;

  const modal =
    document.getElementById(
      "vehicleDeleteConfirmModal"
    );

  showAnimatedModal(modal);
}


function closeVehicleDeleteConfirm(
  event = null
) {

  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const modal =
    document.getElementById(
      "vehicleDeleteConfirmModal"
    );

  hideAnimatedModal(
    modal,
    220,
    function () {

      selectedVehicleDeleteForm = null;
      vehicleDeleteSubmitting = false;

      const button =
        modal.querySelector(".danger-btn");

      button.disabled = false;
      button.innerText = "Yes, Delete";

    }
  );
}


function confirmVehicleDelete(event) {

  event.preventDefault();
  event.stopPropagation();

  if (
    !selectedVehicleDeleteForm ||
    vehicleDeleteSubmitting
  ) {
    return;
  }

  vehicleDeleteSubmitting = true;

  const button = event.currentTarget;

  button.disabled = true;
  button.innerText = "Deleting...";

  selectedVehicleDeleteForm.submit();
}


/* =========================
   INITIALIZATION
========================= */

document.addEventListener(
  "DOMContentLoaded",
  function () {

    const ownership =
      document.getElementById(
        "ownershipTypeInput"
      );

    const status =
      document.getElementById(
        "vehicleStatusInput"
      );

    const vehicleForm =
      document.getElementById(
        "vehicleForm"
      );

    ownership.addEventListener(
      "change",
      updateOwnershipFields
    );

    status.addEventListener(
      "change",
      updateDisposalFields
    );

    vehicleForm.addEventListener(
      "submit",
      function () {

        const submitButton =
          document.getElementById(
            "vehicleSubmitBtn"
          );

        submitButton.disabled = true;
        submitButton.innerText = "Saving...";

      }
    );

    updateOwnershipFields();
    updateDisposalFields();

  }
);