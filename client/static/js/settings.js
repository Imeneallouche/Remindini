document.addEventListener("DOMContentLoaded", function () {
    const sidebarHeader = document.querySelector('.sidebar-header');

  const updatePhoneBtn = document.getElementById("updatePhoneBtn");
  const toggleSmsBtn = document.getElementById("smsToggleBtn");
  const updateReminderBtn = document.getElementById("updateReminderBtn");
  const reminderSettings = document.querySelector(".reminder-duration-item");
  const reminderValue = document.getElementById("reminderValue");
  const reminderUnit = document.getElementById("reminderUnit");

  const tempToggleBtn = document.getElementById("tempToggleBtn");
  const tempThresholdSettings = document.getElementById("tempThresholdSettings");
  const tempThresholdValue = document.getElementById("tempThresholdValue");
  const updateTempThresholdBtn = document.getElementById("updateTempThresholdBtn");

  const humidityToggleBtn = document.getElementById("humidityToggleBtn");
  const humidityThresholdSettings = document.getElementById("humidityThresholdSettings");
  const humidityThresholdValue = document.getElementById("humidityThresholdValue");
  const updateHumidityThresholdBtn = document.getElementById("updateHumidityThresholdBtn");
  

  if (sidebarHeader) {
    sidebarHeader.addEventListener("click", () => {
      window.location.href = "/dashboard";
    });
  }

  function updateReminderUI(data) {
      if (data.reminder_delay !== undefined && data.reminder_unit) {
          let value = data.reminder_delay;
          let unit = data.reminder_unit;

          if (unit === "hours") {
              value = value / 60;
          }

          reminderValue.value = value;
          reminderUnit.value = unit;
      }
  }

  // 🟢 Update Phone Number
  if (updatePhoneBtn) {
      updatePhoneBtn.addEventListener("click", function (event) {
          event.preventDefault();
          let phoneNumber = document.getElementById("phoneNumber").value;

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ phone_number: phoneNumber })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  alert("Phone number updated successfully!");
              } else {
                  alert("Failed to update phone number.");
              }
          })
          .catch(error => console.error("Error:", error));
      });
  }

  // 🟢 Toggle SMS Service
  if (toggleSmsBtn) {
      toggleSmsBtn.addEventListener("click", function () {
          let currentState = toggleSmsBtn.textContent.includes("Disable");
          let newState = !currentState;

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ sms_service_activated: newState })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  toggleSmsBtn.textContent = newState ? "Disable Functionality" : "Enable Functionality";
                  reminderSettings.style.display = newState ? "block" : "none";
                  updateReminderUI(data);
              } else {
                  alert("Failed to update SMS service.");
              }
          })
          .catch(error => console.error("Error:", error));

          
      });
  }

  // 🟢 Update Reminder Settings
  if (updateReminderBtn) {
      updateReminderBtn.addEventListener("click", function (event) {
          event.preventDefault();

          let reminderValueData = parseFloat(reminderValue.value);
          let reminderUnitData = reminderUnit.value;

          if (reminderUnitData === "hours") {
              reminderValueData *= 60;
          }

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  reminder_value: reminderValueData,
                  reminder_unit: reminderUnitData
              })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  alert("Reminder settings updated successfully!");
                  updateReminderUI(data);
              } else {
                  alert("Failed to update reminder settings.");
              }
          })
          .catch(error => console.error("Error:", error));
      });
  }

  // 🟢 Toggle Temperature Monitoring
  if (tempToggleBtn) {
      tempToggleBtn.addEventListener("click", function () {
          let currentState = tempToggleBtn.textContent.includes("Disable");
          let newState = !currentState;

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ temperature_service_activate: newState })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  tempToggleBtn.textContent = newState ? "Disable Functionality" : "Enable Functionality";
                  tempThresholdSettings.style.display = newState ? "block" : "none";
              } else {
                  alert("Failed to update temperature monitoring service.");
              }
          })
          .catch(error => console.error("Error:", error));
      });
  }

  // 🟢 Update Temperature Threshold
  if (updateTempThresholdBtn) {
      updateTempThresholdBtn.addEventListener("click", function (event) {
          event.preventDefault();

          let newThreshold = parseFloat(tempThresholdValue.value);

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ temperature_treshold: newThreshold })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  alert("Temperature threshold updated successfully!");
              } else {
                  alert("Failed to update temperature threshold.");
              }
          })
          .catch(error => console.error("Error:", error));
      });
  }

  // 🟢 Toggle Humidity Monitoring
  if (humidityToggleBtn) {
      humidityToggleBtn.addEventListener("click", function () {
          let currentState = humidityToggleBtn.textContent.includes("Disable");
          let newState = !currentState;

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ humidity_service_activate: newState })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  humidityToggleBtn.textContent = newState ? "Disable Functionality" : "Enable Functionality";
                  humidityThresholdSettings.style.display = newState ? "block" : "none";
              } else {
                  alert("Failed to update humidity monitoring service.");
              }
          })
          .catch(error => console.error("Error:", error));
      });
  }

  // 🟢 Update Humidity Threshold
  if (updateHumidityThresholdBtn) {
      updateHumidityThresholdBtn.addEventListener("click", function (event) {
          event.preventDefault();

          let newThreshold = parseFloat(humidityThresholdValue.value);

          fetch("/settings", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ humidity_treshold: newThreshold })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  alert("Humidity threshold updated successfully!");
              } else {
                  alert("Failed to update humidity threshold.");
              }
          })
          .catch(error => console.error("Error:", error));
      });
  }
});
