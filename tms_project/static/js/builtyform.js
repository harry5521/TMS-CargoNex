// AUTO CALCULATION
const freight =
  document.getElementById(
    "totalFreight"
  );

const advance =
  document.getElementById(
    "advanceAmount"
  );

const remaining =
  document.getElementById(
    "remainingAmount"
  );


function calculateRemaining() {

  const total =
    parseFloat(
      freight.value
    ) || 0;

  const adv =
    parseFloat(
      advance.value
    ) || 0;

  remaining.value =
    total - adv;
}


freight.addEventListener(
  "input",
  calculateRemaining
);

advance.addEventListener(
  "input",
  calculateRemaining
);



// Customer search
let selectedCustomer = null;

const searchInput =
  document.getElementById(
    "customerSearch"
  );

const suggestions =
  document.getElementById(
    "customerSuggestions"
  );

let searchTimer;


searchInput.addEventListener(
    "input",
    function () {

        clearTimeout(searchTimer);

        const query = this.value.trim();

        searchTimer = setTimeout(() => {

            searchCustomers(query);

        }, 300);

    }
);

async function searchCustomers(query) {

    selectedCustomer = null;

    document
        .getElementById("customerId")
        .value = "";

    if (!query) {

        suggestions.innerHTML = "";

        suggestions.style.display = "none";

        return;
    }

    const response = await fetch(
        `/tms/builty/customer-search/?q=${query}`
    );

    const customers =
        await response.json();

    suggestions.innerHTML = "";

    suggestions.style.display =
        customers.length ? "block" : "none";

    customers.forEach(customer => {

        const div =
            document.createElement("div");

        div.className =
            "suggestion-item";

        div.innerText =
            customer.company_name;

        div.onclick = () => {

            selectedCustomer = customer;

            searchInput.value =
                customer.company_name;

            document
                .getElementById("customerId")
                .value =
                customer.id;

            document
                .getElementById("customerPhone")
                .value =
                customer.phone || "";

            document
                .getElementById("customerCnic")
                .value =
                customer.cnic || "";

            suggestions.innerHTML = "";

            suggestions.style.display = "none";
        };

        suggestions.appendChild(div);

    });

}

// Form validation
document
  .querySelector(".form")
  .addEventListener(
    "submit",
    function (e) {

      if (!selectedCustomer) {

        e.preventDefault();

        searchInput.style.border =
          "1px solid #d32f2f";

        searchInput.style.background =
          "#fff5f5";

        document
          .getElementById(
            "customerError"
          )
          .style.display =
          "block";

        return;
      }

    }
  );
