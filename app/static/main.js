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
