function valueOrDash(value) {
  return value && value.trim() !== "" ? value : "—";
}

function getRowFromButton(button) {
  return button.closest(".driver-row");
}


// Helper functions
function showDriverModalSmooth() {
  const modal = document.getElementById("driverModal");

  modal.classList.remove("hidden");

  requestAnimationFrame(function () {
    modal.classList.add("active");
  });
}

function showDriverPanelSmooth() {
  const layout = document.querySelector(".drivers-layout");
  const panel = document.getElementById("driverPanel");

  layout.classList.add("panel-open");
  panel.classList.remove("hidden");

  requestAnimationFrame(function () {
    panel.classList.add("active");
  });
}


function hideDriverPanelSmooth() {
  const layout = document.querySelector(".drivers-layout");
  const panel = document.getElementById("driverPanel");

  panel.classList.remove("active");

  setTimeout(function () {
    panel.classList.add("hidden");
    layout.classList.remove("panel-open");
  }, 280);
}


function hideDriverModalSmooth(callback = null) {
  const modal = document.getElementById("driverModal");

  modal.classList.remove("active");

  setTimeout(function () {
    modal.classList.add("hidden");

    if (callback) {
      callback();
    }

  }, 250);
}


/* =========================
   RIGHT PANEL
========================= */

document.addEventListener("click", function (event) {
  const row = event.target.closest(".driver-row");

  if (!row || event.target.closest(".action-btn")) {
    return;
  }

  openDriverPanel(row);
});


function openDriverPanel(row) {
  showDriverPanelSmooth();

  document.getElementById("panelDriverTitle").innerText =
    row.dataset.fullName;

  document.getElementById("panelDriverCode").innerText =
    valueOrDash(row.dataset.driverCode);

  document.getElementById("panelFullName").innerText =
    valueOrDash(row.dataset.fullName);

  document.getElementById("panelFatherName").innerText =
    valueOrDash(row.dataset.fatherName);

  document.getElementById("panelCnic").innerText =
    valueOrDash(row.dataset.cnic);

  document.getElementById("panelDob").innerText =
    valueOrDash(row.dataset.dateOfBirthDisplay);

  document.getElementById("panelDriverType").innerText =
    valueOrDash(row.dataset.driverTypeDisplay);

  document.getElementById("panelPhone").innerText =
    valueOrDash(row.dataset.phone);

  document.getElementById("panelAlternatePhone").innerText =
    valueOrDash(row.dataset.alternatePhone);

  document.getElementById("panelCity").innerText =
    valueOrDash(row.dataset.city);

  document.getElementById("panelAddress").innerText =
    valueOrDash(row.dataset.address);

  document.getElementById("panelLicenseNo").innerText =
    valueOrDash(row.dataset.licenseNumber);

  document.getElementById("panelLicenseType").innerText =
    valueOrDash(row.dataset.licenseTypeDisplay);

  document.getElementById("panelLicenseIssue").innerText =
    valueOrDash(row.dataset.licenseIssueDateDisplay);

  document.getElementById("panelLicenseExpiry").innerText =
    valueOrDash(row.dataset.licenseExpiryDateDisplay);

  document.getElementById("panelLicenseAuthority").innerText =
    valueOrDash(row.dataset.licenseAuthority);

  document.getElementById("panelEmergencyName").innerText =
    valueOrDash(row.dataset.emergencyContactName);

  document.getElementById("panelEmergencyPhone").innerText =
    valueOrDash(row.dataset.emergencyContactPhone);

  document.getElementById("panelStatus").innerText =
    valueOrDash(row.dataset.statusDisplay);

  document.getElementById("panelJoiningDate").innerText =
    valueOrDash(row.dataset.joiningDateDisplay);

  document.getElementById("panelNotes").innerText =
    valueOrDash(row.dataset.notes);
}


function closeDriverPanel() {
  hideDriverPanelSmooth();
}

/* =========================
   CREATE / EDIT MODAL
========================= */

function openDriverModal(button = null) {
  const modal = document.getElementById("driverModal");
  const form = document.getElementById("driverForm");
  const title = document.getElementById("driverModalTitle");
  const submitBtn = document.getElementById("driverSubmitBtn");

  showDriverModalSmooth();
  form.reset();

  if (!button) {
    title.innerText = "Add Driver";
    submitBtn.innerText = "Save Driver";
    form.action = form.dataset.createUrl;
    return;
  }

  const row = getRowFromButton(button);

  title.innerText = "Edit Driver";
  submitBtn.innerText = "Update Driver";
  form.action = row.dataset.updateUrl;

  document.getElementById("fullNameInput").value =
    row.dataset.fullName || "";

  document.getElementById("fatherNameInput").value =
    row.dataset.fatherName || "";

  document.getElementById("cnicInput").value =
    row.dataset.cnic || "";

  document.getElementById("dobInput").value =
    row.dataset.dateOfBirth || "";

  document.getElementById("driverTypeInput").value =
    row.dataset.driverType || "company";

  document.getElementById("phoneInput").value =
    row.dataset.phone || "";

  document.getElementById("alternatePhoneInput").value =
    row.dataset.alternatePhone || "";

  document.getElementById("cityInput").value =
    row.dataset.city || "";

  document.getElementById("addressInput").value =
    row.dataset.address || "";

  document.getElementById("emergencyNameInput").value =
    row.dataset.emergencyContactName || "";

  document.getElementById("emergencyPhoneInput").value =
    row.dataset.emergencyContactPhone || "";

  document.getElementById("licenseNumberInput").value =
    row.dataset.licenseNumber || "";

  document.getElementById("licenseTypeInput").value =
    row.dataset.licenseType || "htv";

  document.getElementById("licenseIssueInput").value =
    row.dataset.licenseIssueDate || "";

  document.getElementById("licenseExpiryInput").value =
    row.dataset.licenseExpiryDate || "";

  document.getElementById("licenseAuthorityInput").value =
    row.dataset.licenseAuthority || "";

  document.getElementById("joiningDateInput").value =
    row.dataset.joiningDate || "";

  document.getElementById("statusInput").value =
    row.dataset.status || "active";

  document.getElementById("notesInput").value =
    row.dataset.notes || "";
}


function closeDriverModal() {
  const form = document.getElementById("driverForm");

  hideDriverModalSmooth(function () {

    if (form) {
      form.reset();
      form.action = form.dataset.createUrl;
    }

  });
}

let selectedDriverDeleteForm = null;
let deleteDriverSubmitting = false;


function openDeleteDriverConfirm(event, button) {

  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  if (!button || typeof button.closest !== "function") {
    return;
  }

  deleteDriverSubmitting = false;

  selectedDriverDeleteForm =
    button.closest(".driver-delete-form");

  const row =
    button.closest(".driver-row");

  const driverName =
    row?.dataset.fullName || "this driver";

  const driverCode =
    row?.dataset.driverCode || "";

  const nameBox =
    document.getElementById("deleteDriverName");

  if (nameBox) {
    nameBox.innerText =
      driverCode
        ? `${driverName} (${driverCode})`
        : driverName;
  }

  const modal =
    document.getElementById("deleteDriverConfirmModal");

  if (!modal) {
    return;
  }

  modal.classList.remove("hidden");

  requestAnimationFrame(function () {
    modal.classList.add("active");
  });
}


function closeDeleteDriverConfirm(event = null) {

  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const modal =
    document.getElementById("deleteDriverConfirmModal");

  if (!modal) {
    return;
  }

  modal.classList.remove("active");

  setTimeout(function () {

    modal.classList.add("hidden");
    selectedDriverDeleteForm = null;
    deleteDriverSubmitting = false;

    const confirmBtn =
      modal.querySelector(".danger-btn");

    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.innerText = "Yes, Delete";
    }

  }, 220);
}


function confirmDeleteDriver(event) {

  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  if (
    !selectedDriverDeleteForm ||
    deleteDriverSubmitting
  ) {
    return;
  }

  deleteDriverSubmitting = true;

  const confirmBtn =
    event?.currentTarget;

  if (confirmBtn) {
    confirmBtn.disabled = true;
    confirmBtn.innerText = "Deleting...";
  }

  selectedDriverDeleteForm.submit();
}