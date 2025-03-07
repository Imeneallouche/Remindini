// settings.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM Elements
const smsToggleBtn = document.getElementById("smsToggleBtn");
const tempToggleBtn = document.getElementById("tempToggleBtn");
const phoneNumberInput = document.getElementById("phoneNumber");
const updatePhoneBtn = document.getElementById("updatePhoneBtn");

// We'll store the current statuses in memory
let smsEnabled = false;
let tempEnabled = false;

document.addEventListener("DOMContentLoaded", () => {
  // 1. Fetch current settings from the server
  fetchSettings();

  // 2. Add event listeners
  smsToggleBtn.addEventListener("click", toggleSmsFunctionality);
  tempToggleBtn.addEventListener("click", toggleTempFunctionality);
  updatePhoneBtn.addEventListener("click", updatePhoneNumber);
});

/**
 * Fetches the current status of functionalities and user phone number
 * from the server, then updates the UI.
 */
async function fetchSettings() {
  try {
    const response = await fetch(`${SERVER_URL}/api/settings`);
    if (!response.ok) {
      throw new Error(`Error fetching settings: ${response.status}`);
    }
    const data = await response.json();
    // data = {
    //   smsRemindersEnabled: true/false,
    //   realTimeTempEnabled: true/false,
    //   phoneNumber: "+1 2025550136"
    // }
    smsEnabled = data.smsRemindersEnabled;
    tempEnabled = data.realTimeTempEnabled;

    // Update button text
    smsToggleBtn.textContent = smsEnabled
      ? "Disable Functionality"
      : "Enable Functionality";
    tempToggleBtn.textContent = tempEnabled
      ? "Disable Functionality"
      : "Enable Functionality";

    // Update phone number placeholder
    phoneNumberInput.placeholder = data.phoneNumber || "+1 2025550136";
  } catch (error) {
    console.error(error);
  }
}

/**
 * Toggles the SMS Reminders functionality on the server,
 * then updates the button text.
 */
async function toggleSmsFunctionality() {
  try {
    // We'll send a PATCH or POST request to toggle
    const newStatus = !smsEnabled;
    const response = await fetch(`${SERVER_URL}/api/settings/sms-reminders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: newStatus }),
    });
    if (!response.ok) {
      throw new Error(`Error toggling SMS Reminders: ${response.status}`);
    }
    const data = await response.json();
    // data = { smsRemindersEnabled: true/false }

    smsEnabled = data.smsRemindersEnabled;
    smsToggleBtn.textContent = smsEnabled
      ? "Disable Functionality"
      : "Enable Functionality";
  } catch (error) {
    console.error(error);
    alert("Failed to toggle SMS reminders. Please try again.");
  }
}

/**
 * Toggles the Real-Time Temperature Monitoring functionality
 */
async function toggleTempFunctionality() {
  try {
    const newStatus = !tempEnabled;
    const response = await fetch(`${SERVER_URL}/api/settings/real-time-temp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: newStatus }),
    });
    if (!response.ok) {
      throw new Error(`Error toggling Real-Time Temp: ${response.status}`);
    }
    const data = await response.json();
    // data = { realTimeTempEnabled: true/false }

    tempEnabled = data.realTimeTempEnabled;
    tempToggleBtn.textContent = tempEnabled
      ? "Disable Functionality"
      : "Enable Functionality";
  } catch (error) {
    console.error(error);
    alert(
      "Failed to toggle Real-Time Temperature Monitoring. Please try again."
    );
  }
}

/**
 * Updates the user's phone number in the database
 */
async function updatePhoneNumber() {
  const newPhoneNumber = phoneNumberInput.value.trim();
  if (!newPhoneNumber) {
    alert("Please enter a valid phone number.");
    return;
  }

  try {
    const response = await fetch(`${SERVER_URL}/api/settings/phone-number`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phoneNumber: newPhoneNumber }),
    });
    if (!response.ok) {
      throw new Error(`Error updating phone number: ${response.status}`);
    }
    const data = await response.json();
    // data = { success: true, phoneNumber: "...", message: "Phone number updated" }

    alert(data.message || "Phone number updated successfully.");
    // Update placeholder
    phoneNumberInput.placeholder = data.phoneNumber;
    // Clear the input field
    phoneNumberInput.value = "";
  } catch (error) {
    console.error(error);
    alert("Failed to update phone number. Please try again.");
  }
}
