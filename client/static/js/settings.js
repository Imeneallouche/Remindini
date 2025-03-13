// settings.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM elements
const smsToggleBtn = document.getElementById("smsToggleBtn");
const tempToggleBtn = document.getElementById("tempToggleBtn");
const humidityToggleBtn = document.getElementById("humidityToggleBtn");
const phoneNumberInput = document.getElementById("phoneNumber");
const updatePhoneBtn = document.getElementById("updatePhoneBtn");

const reminderDurationItem = document.querySelector(".reminder-duration-item");
const reminderValueInput = document.getElementById("reminderValue");
const reminderUnitSelect = document.getElementById("reminderUnit");
const updateReminderBtn = document.getElementById("updateReminderBtn");

// Threshold setting elements
const tempThresholdSettings = document.getElementById("tempThresholdSettings");
const tempThresholdValue = document.getElementById("tempThresholdValue");
const updateTempThresholdBtn = document.getElementById("updateTempThresholdBtn");

const humidityThresholdSettings = document.getElementById("humidityThresholdSettings");
const humidityThresholdValue = document.getElementById("humidityThresholdValue");
const updateHumidityThresholdBtn = document.getElementById("updateHumidityThresholdBtn");

const signOutBtn = document.getElementById("signOutBtn");

// Sidebar header element
const sidebarHeader = document.querySelector(".sidebar-header");

// State variables
let smsEnabled = false;
let tempEnabled = false;
let humidityEnabled = false;
let currentPhoneNumber = "";
let currentReminderValue = 2;
let currentReminderUnit = "hours";
let currentTempThreshold = 25;
let currentHumidityThreshold = 60;

document.addEventListener("DOMContentLoaded", () => {
  // 1. Fetch current settings from server
  fetchSettings();

  // 2. Set up event listeners
  smsToggleBtn.addEventListener("click", toggleSmsReminders);
  tempToggleBtn.addEventListener("click", toggleRealTimeTemp);
  humidityToggleBtn.addEventListener("click", toggleRealTimeHumidity);
  updatePhoneBtn.addEventListener("click", updatePhoneNumber);
  updateReminderBtn.addEventListener("click", updateReminderDuration);
  updateTempThresholdBtn.addEventListener("click", updateTempThreshold);
  updateHumidityThresholdBtn.addEventListener("click", updateHumidityThreshold);

  // 3. Add click event for sidebar header to navigate to dashboard
  sidebarHeader.addEventListener("click", () => {
    window.location.href = "/dashboard";
  });

  // Optional: sign out logic
  if (signOutBtn) {
    signOutBtn.addEventListener("click", () => {
      // For example, call a logout endpoint or clear session
      window.location.href = "signin.html";
    });
  }
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
    //   realTimeHumidityEnabled: false,
    //   phoneNumber: "+1 2025550136",
    //   reminderValue: 2,
    //   reminderUnit: "hours",
    //   tempThreshold: 25,
    //   humidityThreshold: 60
    // }

    smsEnabled = data.smsRemindersEnabled;
    tempEnabled = data.realTimeTempEnabled;
    humidityEnabled = data.realTimeHumidityEnabled || false;
    currentPhoneNumber = data.phoneNumber || "+1 2025550136";
    currentReminderValue = data.reminderValue || 2;
    currentReminderUnit = data.reminderUnit || "hours";
    currentTempThreshold = data.tempThreshold || 25;
    currentHumidityThreshold = data.humidityThreshold || 60;

    // Update UI
    updateSmsToggleButton();
    toggleReminderDurationVisibility();

    updateTempToggleButton();
    toggleTempThresholdVisibility();

    updateHumidityToggleButton();
    toggleHumidityThresholdVisibility();

    phoneNumberInput.placeholder = currentPhoneNumber;

    reminderValueInput.value = currentReminderValue;
    reminderUnitSelect.value = currentReminderUnit;
    tempThresholdValue.value = currentTempThreshold;
    humidityThresholdValue.value = currentHumidityThreshold;
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

    updateSmsToggleButton();
    toggleReminderDurationVisibility();
  } catch (error) {
    console.error(error);
    alert("Failed to toggle SMS reminders. Please try again.");
  }
}

/**
 * Update the SMS toggle button text and reminder duration visibility
 */
function updateSmsToggleButton() {
  smsToggleBtn.textContent = smsEnabled
    ? "Disable Functionality"
    : "Enable Functionality";
}

/**
 * Toggle the visibility of the reminder duration section
 * based on SMS reminders enabled status
 */
function toggleReminderDurationVisibility() {
  if (smsEnabled) {
    reminderDurationItem.style.display = 'block';
  } else {
    reminderDurationItem.style.display = 'none';
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

    updateTempToggleButton();
    toggleTempThresholdVisibility();
  } catch (error) {
    console.error(error);
    alert("Failed to toggle real-time temperature. Please try again.");
  }
}

/**
 * Update the temperature toggle button text
 */
function updateTempToggleButton() {
  tempToggleBtn.textContent = tempEnabled
    ? "Disable Functionality"
    : "Enable Functionality";
}

/**
 * Toggle the visibility of the temperature threshold section
 */
function toggleTempThresholdVisibility() {
  if (tempEnabled) {
    tempThresholdSettings.style.display = 'block';
  } else {
    tempThresholdSettings.style.display = 'none';
  }
}

/**
 * Update the Temperature Threshold
 */
async function updateTempThreshold() {
  const value = parseInt(tempThresholdValue.value, 10);

  if (isNaN(value)) {
    alert("Please enter a valid temperature threshold.");
    return;
  }

  try {
    const response = await fetch(
      `${SERVER_URL}/api/settings/temp-threshold`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ threshold: value }),
      }
    );
    if (!response.ok) {
      throw new Error(`Error updating temperature threshold: ${response.status}`);
    }
    const data = await response.json();
    alert(data.message || "Temperature threshold updated successfully.");

    currentTempThreshold = data.tempThreshold;
    tempThresholdValue.value = currentTempThreshold;
  } catch (error) {
    console.error(error);
    alert("Failed to update temperature threshold. Please try again.");
  }
}

/**
 * Toggle Real-Time Humidity Monitoring
 */
async function toggleRealTimeHumidity() {
  const newStatus = !humidityEnabled;
  try {
    const response = await fetch(`${SERVER_URL}/api/settings/real-time-humidity`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: newStatus }),
    });
    if (!response.ok) {
      throw new Error(`Error toggling real-time humidity: ${response.status}`);
    }
    const data = await response.json();
    humidityEnabled = data.realTimeHumidityEnabled;

    updateHumidityToggleButton();
    toggleHumidityThresholdVisibility();
  } catch (error) {
    console.error(error);
    alert("Failed to toggle real-time humidity. Please try again.");
  }
}

/**
 * Update the humidity toggle button text
 */
function updateHumidityToggleButton() {
  humidityToggleBtn.textContent = humidityEnabled
    ? "Disable Functionality"
    : "Enable Functionality";
}

/**
 * Toggle the visibility of the humidity threshold section
 */
function toggleHumidityThresholdVisibility() {
  if (humidityEnabled) {
    humidityThresholdSettings.style.display = 'block';
  } else {
    humidityThresholdSettings.style.display = 'none';
  }
}

/**
 * Update the Humidity Threshold
 */
async function updateHumidityThreshold() {
  const value = parseInt(humidityThresholdValue.value, 10);

  if (isNaN(value) || value < 0 || value > 100) {
    alert("Please enter a valid humidity threshold (0-100%).");
    return;
  }

  try {
    const response = await fetch(
      `${SERVER_URL}/api/settings/humidity-threshold`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ threshold: value }),
      }
    );
    if (!response.ok) {
      throw new Error(`Error updating humidity threshold: ${response.status}`);
    }
    const data = await response.json();
    alert(data.message || "Humidity threshold updated successfully.");

    currentHumidityThreshold = data.humidityThreshold;
    humidityThresholdValue.value = currentHumidityThreshold;
  } catch (error) {
    console.error(error);
    alert("Failed to update humidity threshold. Please try again.");
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