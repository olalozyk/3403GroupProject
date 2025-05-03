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

//-------------------for deletion--------------------
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
//-------------------for deletion--------------------
