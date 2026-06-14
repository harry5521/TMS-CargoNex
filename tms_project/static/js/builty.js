let currentRow = null;


/* ROW CLICK */
document.addEventListener("click", function (e) {

    const row = e.target.closest("tbody tr");

    if (!row) return;

    currentRow = row;

    openBuiltyPanel(row);

});


/* OPEN PANEL */
function openBuiltyPanel(row) {

    document
        .getElementById("builtyPanel")
        .classList
        .remove("hidden");


    document.getElementById("builtyTitle").innerText =
        row.dataset.no + " Details";

    document.getElementById("bDate").innerText =
        row.dataset.date;

    document.getElementById("bCustomer").innerText =
        row.dataset.customer;

    document.getElementById("bPhone").innerText =
        row.dataset.phone || "-";

    document.getElementById("bRoute").innerText =
        row.dataset.route;

    document.getElementById("bReceiver").innerText =
        row.dataset.receiver;

    document.getElementById("bReceiverPhone").innerText =
        row.dataset.receiverPhone || "-";

    document.getElementById("bFreight").innerText =
        "PKR " + row.dataset.freight;

    document.getElementById("bAdvance").innerText =
        "PKR " + row.dataset.advance;

    document.getElementById("bRemaining").innerText =
        "PKR " + row.dataset.remaining;

    document.getElementById("bPaymentStatus").innerText =
        row.dataset.payment;

    document.getElementById("bDispatchStatus").innerText =
        row.dataset.dispatch;

    document.getElementById("bVehicle").innerText =
        row.dataset.vehicle || "-";

    document.getElementById("bDriver").innerText =
        row.dataset.driver || "-";

    document.getElementById("bDriverPhone").innerText =
        row.dataset.driverPhone || "-";

    document.getElementById("bNotes").innerText =
        row.dataset.notes || "-";
}


/* CLOSE PANEL */
function closeBuilty() {

    document
        .getElementById("builtyPanel")
        .classList
        .add("hidden");

}