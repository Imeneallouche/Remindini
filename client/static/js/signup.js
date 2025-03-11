function showPopup(message) {
    const popup = document.getElementById("errorPopup");
    document.getElementById("errorMessage").textContent = message;
    popup.style.display = "block";

    // Hide the popup after 5 seconds
    setTimeout(() => {
      popup.style.display = "none";
    }, 6000);
  }

  function closePopup() {
    document.getElementById("errorPopup").style.display = "none";
  }

  // Check if there's an error from the backend
  window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get("error");
    if (error) {
      showPopup(error);
    }
  };