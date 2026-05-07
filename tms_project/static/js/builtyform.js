// AUTO CALCULATION
const total = document.getElementById("total");
const advance = document.getElementById("advance");
const remaining = document.getElementById("remaining");

function calculate() {
  const t = parseFloat(total.value) || 0;
  const a = parseFloat(advance.value) || 0;
  remaining.value = t - a;
}

total.addEventListener("input", calculate);
advance.addEventListener("input", calculate);



// PAYMENT TOGGLE
document.querySelectorAll(".payment-toggle button").forEach(btn => {
  btn.addEventListener("click", function () {
    document.querySelectorAll(".payment-toggle button").forEach(b => b.classList.remove("active"));
    this.classList.add("active");
  });
});
// Select the first button and click it to trigger the logic
document.querySelector(".payment-toggle button")?.click();
