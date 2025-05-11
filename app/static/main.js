//---------------eye icon--------------------------
document.querySelectorAll(".toggle-password").forEach(function (toggleIcon) {
  toggleIcon.addEventListener("click", function () {
    const targetId = this.getAttribute("data-target");
    const input = document.getElementById(targetId);

    const type =
      input.getAttribute("type") === "password" ? "text" : "password";
    input.setAttribute("type", type);

    this.classList.toggle("bi-eye");
    this.classList.toggle("bi-eye-slash");
  });
});
//---------------eye icon--------------------------

// -------for featured slider--------
const featuredSwiper = new Swiper(".featured-slider", {
  autoplay: {
    delay: 3000,
    disableOnInteraction: false,
  },
  loop: true,
  pagination: {
    el: ".featured-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".featured-next",
    prevEl: ".featured-prev",
  },
});
// -------for featured slider--------

//-------------------for appointment deletion--------------------
const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute("content");

function deleteAppointment(appointmentId) {
  fetch(`/appointment/delete/${appointmentId}`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}), // You can include data if needed
  }).then((response) => {
    if (response.ok) {
      location.reload(); // or remove the row from the DOM
    } else {
      alert("Failed to delete appointment");
    }
  });
}
//-------------------for appointment deletion--------------------

//-------------------for notification--------------------
document.addEventListener("DOMContentLoaded", function () {
  const notificationLink = document.querySelector("#notification-link");
  if (notificationLink) {
    notificationLink.addEventListener("show.bs.dropdown", function () {
      fetch("/notifications/read", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document
            .querySelector('meta[name="csrf-token"]')
            .getAttribute("content"),
        },
        body: JSON.stringify({}),
      }).then((res) => {
        if (res.ok) {
          // Hide badge immediately
          const badge = document.querySelector(".badge.bg-danger");
          if (badge) {
            badge.remove();
          }
        }
      });
    });
  }
});
//-------------------for notification--------------------

//-------------------for socket--------------------
const socket = io();

socket.on("connect", () => {
  console.log("Connected to SocketIO server");

  // Emit a test login event
  socket.emit("login_event", { message: "Client login test" });
});

socket.on("user_connected", (data) => {
  console.log("User connected:", data);
});

socket.on("login_broadcast", (data) => {
  console.log("Broadcast:", data);
});

socket.on("unauthorized", () => {
  console.log("Unauthorized SocketIO access");
});

socket.on("disconnect", () => {
  console.log("Disconnected from server");
});
//-------------------for socket--------------------

//-------------------for Appointment Frequency line chart--------------------
document.addEventListener("DOMContentLoaded", () => {
  const raw = document.getElementById("line-data")?.textContent;
  const chartData = JSON.parse(raw);
  const ctx = document
    .getElementById("appointmentFrequencyChart")
    .getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Appointment Frequencies",
          font: { size: 24 },
          color: "#4B0082",
        },
        legend: {
          position: "bottom",
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 10, // force max range
          ticks: {
            stepSize: 2,
          },
          title: {
            display: true,
            text: "No. of Appointments",
            font: {
              size: 18,
            },
          },
        },
        x: {
          title: {
            display: true,
            text: "Months",
            font: {
              size: 18,
            },
          },
        },
      },
    },
  }); // close new Chart
});
//-------------------for Appointment Frequency line chart--------------------

//-------------------for counter effect--------------------
document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".counter");
  const speed = 120; // lower = faster

  counters.forEach((counter) => {
    const updateCount = () => {
      const target = +counter.getAttribute("data-target");
      const count = +counter.innerText;
      const increment = Math.ceil(target / speed);

      if (count < target) {
        counter.innerText = count + increment;
        setTimeout(updateCount, 20);
      } else {
        counter.innerText = target;
      }
    };

    updateCount();
  });
});
//-------------------for counter effect--------------------
