// dashboard.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM elements to update
const smsSuccessCountEl = document.getElementById("smsSuccessCount");
const smsFailedCountEl = document.getElementById("smsFailedCount");
const currentTemperatureEl = document.getElementById("currentTemperature");

document.addEventListener("DOMContentLoaded", () => {
  // 1. Fetch SMS stats
  fetchSmsStats();

  // 2. Fetch current temperature initially
  fetchCurrentTemperature();

  // 3. Set interval to update temperature in real time (every 5 seconds)
  setInterval(fetchCurrentTemperature, 5000);
});

/**
 * Fetches the number of SMS sent successfully and the number that failed
 * from the backend for the current week.
 */
async function fetchSmsStats() {
  try {
    const response = await fetch(`${SERVER_URL}/api/sms-stats?week=current`);
    if (!response.ok) {
      throw new Error(`Error fetching SMS stats: ${response.status}`);
    }
    const data = await response.json();
    // Suppose data = { successCount: 10, failCount: 1 }
    smsSuccessCountEl.textContent = `${data.successCount} SMS`;
    smsFailedCountEl.textContent = `${data.failCount} SMS`;
  } catch (error) {
    console.error(error);
  }
}

/**
 * Fetches the current temperature from the Raspberry Pi's sensor
 * via the backend, and updates the UI.
 */
async function fetchCurrentTemperature() {
  try {
    const response = await fetch(`${SERVER_URL}/api/current-temperature`);
    if (!response.ok) {
      throw new Error(`Error fetching temperature: ${response.status}`);
    }
    const data = await response.json();
    // Suppose data = { temperature: 26 }
    currentTemperatureEl.textContent = `${data.temperature}°C`;
  } catch (error) {
    console.error(error);
  }
}
