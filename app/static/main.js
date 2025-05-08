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
