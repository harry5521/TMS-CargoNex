// STATUS TOGGLE
const statusButtons = document.querySelectorAll(".status-toggle button");

statusButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    statusButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  });
});


// FORM SUBMIT
document.querySelector(".form-container").addEventListener("submit", function(e) {
  e.preventDefault();

  const name = document.querySelector('input[placeholder="e.g. ABC Logistics"]').value;
  const phone = document.querySelector('input[placeholder="+92 3xx xxxxxxx"]').value;
  const type = document.querySelector("select").value;

  const status = document.querySelector(".status-toggle .active").innerText;

  if (!name) {
    alert("Customer name is required!");
    return;
  }

  const customerData = {
    name,
    phone,
    type,
    status
  };

  console.log("Customer Saved:", customerData);

  alert("Customer saved successfully ✅");
});