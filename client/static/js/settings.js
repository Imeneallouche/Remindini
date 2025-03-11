// settings.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM elements
const smsToggleBtn = document.getElementById("smsToggleBtn");
const tempToggleBtn = document.getElementById("tempToggleBtn");
const phoneNumberInput = document.getElementById("phoneNumber");
const updatePhoneBtn = document.getElementById("updatePhoneBtn");

const reminderValueInput = document.getElementById("reminderValue");
const reminderUnitSelect = document.getElementById("reminderUnit");
const updateReminderBtn = document.getElementById("updateReminderBtn");

const signOutBtn = document.getElementById("signOutBtn");

// State variables
let smsEnabled = false;
let tempEnabled = false;
let currentPhoneNumber = "";
let currentReminderValue = 2;
let currentReminderUnit = "hours";

document.addEventListener("DOMContentLoaded", () => {
  // 1. Fetch current settings from server
  fetchSettings();

  // 2. Set up event listeners
  smsToggleBtn.addEventListener("click", toggleSmsReminders);
  tempToggleBtn.addEventListener("click", toggleRealTimeTemp);
  updatePhoneBtn.addEventListener("click", updatePhoneNumber);
  updateReminderBtn.addEventListener("click", updateReminderDuration);

  // Optional: sign out logic
  signOutBtn.addEventListener("click", () => {
    // For example, call a logout endpoint or clear session
    window.location.href = "signin.html";
  });
});

/**
 * Fetch the current settings from the server
 */
async function fetchSettings() {
  try {
    const response = await fetch(`${SERVER_URL}/api/settings`);
    if (!response.ok) {
      throw new Error(`Error fetching settings: ${response.status}`);
    }
    const data = await response.json();
    // data might look like:
    // {
    //   smsRemindersEnabled: true,
    //   realTimeTempEnabled: false,
    //   phoneNumber: "+1 2025550136",
    //   reminderValue: 2,
    //   reminderUnit: "hours"
    // }

    smsEnabled = data.smsRemindersEnabled;
    tempEnabled = data.realTimeTempEnabled;
    currentPhoneNumber = data.phoneNumber || "+1 2025550136";
    currentReminderValue = data.reminderValue || 2;
    currentReminderUnit = data.reminderUnit || "hours";

    // Update UI
    smsToggleBtn.textContent = smsEnabled
      ? "Disable Functionality"
      : "Enable Functionality";

    tempToggleBtn.textContent = tempEnabled
      ? "Disable Functionality"
      : "Enable Functionality";

    phoneNumberInput.placeholder = currentPhoneNumber;

    reminderValueInput.value = currentReminderValue;
    reminderUnitSelect.value = currentReminderUnit;
  } catch (error) {
    console.error(error);
  }
}

/**
 * Toggle SMS Reminders functionality
 */
async function toggleSmsReminders() {
  const newStatus = !smsEnabled;
  try {
    const response = await fetch(`${SERVER_URL}/api/settings/sms-reminders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: newStatus }),
    });
    if (!response.ok) {
      throw new Error(`Error toggling SMS reminders: ${response.status}`);
    }
    const data = await response.json();
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
 * Update the SMS Reminder Duration
 */
async function updateReminderDuration() {
  const value = parseInt(reminderValueInput.value, 10);
  const unit = reminderUnitSelect.value;

  if (isNaN(value) || value < 0) {
    alert("Please enter a valid reminder value.");
    return;
  }

  try {
    const response = await fetch(
      `${SERVER_URL}/api/settings/reminder-duration`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value, unit }),
      }
    );
    if (!response.ok) {
      throw new Error(`Error updating reminder duration: ${response.status}`);
    }
    const data = await response.json();
    // data = { reminderValue: number, reminderUnit: string, message: "..."}
    alert(data.message || "Reminder duration updated successfully.");

    currentReminderValue = data.reminderValue;
    currentReminderUnit = data.reminderUnit;
    reminderValueInput.value = currentReminderValue;
    reminderUnitSelect.value = currentReminderUnit;
  } catch (error) {
    console.error(error);
    alert("Failed to update reminder duration. Please try again.");
  }
}

/**
 * Toggle Real-Time Temperature Monitoring
 */
async function toggleRealTimeTemp() {
  const newStatus = !tempEnabled;
  try {
    const response = await fetch(`${SERVER_URL}/api/settings/real-time-temp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: newStatus }),
    });
    if (!response.ok) {
      throw new Error(`Error toggling real-time temp: ${response.status}`);
    }
    const data = await response.json();
    tempEnabled = data.realTimeTempEnabled;

    tempToggleBtn.textContent = tempEnabled
      ? "Disable Functionality"
      : "Enable Functionality";
  } catch (error) {
    console.error(error);
    alert("Failed to toggle real-time temperature. Please try again.");
  }
}

/**
 * Update the user's phone number
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
    // data = { phoneNumber: "...", message: "Phone number updated" }
    alert(data.message || "Phone number updated successfully.");

    currentPhoneNumber = data.phoneNumber;
    phoneNumberInput.placeholder = currentPhoneNumber;
    phoneNumberInput.value = "";
  } catch (error) {
    console.error(error);
    alert("Failed to update phone number. Please try again.");
  }
}
