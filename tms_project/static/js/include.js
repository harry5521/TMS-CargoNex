
// ✅ ACTIVE SIDEBAR LOGIC
function setActiveSidebar() {
  const currentPath = window.location.pathname.split("/").pop(); // get file name only

  document.querySelectorAll(".side-bar-item a").forEach(link => {
    const linkPath = link.getAttribute("href").split("/").pop();

    if (linkPath === currentPath) {
      link.parentElement.classList.add("active");
    }
  });
}


// Filter JS

/* ON PAGE LOAD */
document.addEventListener("DOMContentLoaded", function () {
  handleFilterChange(); // only UI control, no filtering
});

/* HANDLE SELECT CHANGE */
function handleFilterChange() {
  const value = document.getElementById("filterSelect").value;
  const dateBox = document.getElementById("dateRangeBox");

  if (value === "range") {
    dateBox.classList.remove("hidden");
  } else {
    dateBox.classList.add("hidden");
  }
}

/***************************
 PAGINATION LOGIC
***************************/
// const rowsPerPage = 10;
// let currentPage = 1;

// function setupPagination() {
//   const rows = document.querySelectorAll("tbody tr");
//   const totalPages = Math.ceil(rows.length / rowsPerPage);

//   renderTablePage(1);
//   renderPaginationButtons(totalPages);
// }

// function renderTablePage(page) {
//   const rows = document.querySelectorAll("tbody tr");
//   currentPage = page;

//   const start = (page - 1) * rowsPerPage;
//   const end = start + rowsPerPage;

//   rows.forEach((row, index) => {
//     row.style.display = (index >= start && index < end) ? "" : "none";
//   });
// }

// function renderPaginationButtons(totalPages) {
//   const container = document.getElementById("pagination");
//   container.innerHTML = "";

//   // PREV BUTTON
//   const prev = document.createElement("button");
//   prev.innerText = "Prev";
//   prev.onclick = () => {
//     if (currentPage > 1) {
//       renderTablePage(currentPage - 1);
//       updateActiveButton();
//     }
//   };
//   container.appendChild(prev);

//   // PAGE NUMBERS
//   for (let i = 1; i <= totalPages; i++) {
//     const btn = document.createElement("button");
//     btn.innerText = i;

//     btn.onclick = () => {
//       renderTablePage(i);
//       updateActiveButton();
//     };

//     container.appendChild(btn);
//   }

//   // NEXT BUTTON
//   const next = document.createElement("button");
//   next.innerText = "Next";
//   next.onclick = () => {
//     if (currentPage < totalPages) {
//       renderTablePage(currentPage + 1);
//       updateActiveButton();
//     }
//   };
//   container.appendChild(next);

//   updateActiveButton();
// }

// function updateActiveButton() {
//   const buttons = document.querySelectorAll(".pagination button");

//   buttons.forEach(btn => {
//     btn.classList.remove("active");

//     if (parseInt(btn.innerText) === currentPage) {
//       btn.classList.add("active");
//     }
//   });
// }

// /* INIT PAGINATION AFTER PAGE LOAD */
// document.addEventListener("DOMContentLoaded", function () {
//   setupPagination();
// });