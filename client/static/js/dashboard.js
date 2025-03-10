// dashboard.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM elements for SMS stats
const smsSuccessCountEl = document.getElementById("smsSuccessCount");
const smsFailedCountEl = document.getElementById("smsFailedCount");

// DOM elements for temperature
const currentTemperatureEl = document.getElementById("currentTemperature");

// DOM elements for chart
let tempChart;
const durationValueInput = document.getElementById("durationValue");
const durationUnitSelect = document.getElementById("durationUnit");
const updateDurationBtn = document.getElementById("updateDurationBtn");

document.addEventListener("DOMContentLoaded", () => {
  // 1. Fetch SMS stats
  fetchSmsStats();

  // 2. Set up the real-time temperature fetch
  fetchCurrentTemperature();
  setInterval(fetchCurrentTemperature, 5000); // Update every 5 seconds

  // 3. Initialize the chart
  initChart();

  // 4. Fetch initial temperature history
  fetchTemperatureHistory();

  // 5. Handle the "Update" button for chart duration
  updateDurationBtn.addEventListener("click", () => {
    fetchTemperatureHistory();
  });
});

/**
 * Fetches the SMS stats (success/fail) for the current week.
 */
async function fetchSmsStats() {
  try {
    const response = await fetch(`${SERVER_URL}/api/sms-stats?week=current`);
    if (!response.ok) {
      throw new Error(`Error fetching SMS stats: ${response.status}`);
    }
    const data = await response.json();
    // Suppose data = { successCount: 10, failCount: 2 }
    smsSuccessCountEl.textContent = `${data.successCount} SMS`;
    smsFailedCountEl.textContent = `${data.failCount} SMS`;
  } catch (error) {
    console.error(error);
  }
}

/**
 * Fetches the current temperature from the server.
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

/**
 * Initializes the Chart.js line chart.
 */
function initChart() {
  const ctx = document.getElementById("tempChart").getContext("2d");
  tempChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Temperature (°C)",
          data: [],
          fill: false,
          borderColor: "#4285f4",
          tension: 0.1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
        },
        y: {
          title: {
            display: true,
            text: "Temperature (°C)",
          },
          beginAtZero: false,
        },
      },
    },
  });
}

/**
 * Fetches the temperature history for the chosen duration.
 */
async function fetchTemperatureHistory() {
  const value = parseInt(durationValueInput.value, 10);
  const unit = durationUnitSelect.value;

  try {
    // GET /api/temperature-history?value=1&unit=week
    const response = await fetch(
      `${SERVER_URL}/api/temperature-history?value=${value}&unit=${unit}`
    );
    if (!response.ok) {
      throw new Error(`Error fetching temperature history: ${response.status}`);
    }
    const data = await response.json();
    // data = [
    //   { timestamp: "2025-03-01T12:00:00", temperature: 25.5 },
    //   ...
    // ]
    updateChart(data);
  } catch (error) {
    console.error(error);
  }
}

/**
 * Updates the chart with the fetched historical data.
 */
function updateChart(historyData) {
  // Sort by timestamp if not already
  historyData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const labels = historyData.map((entry) => {
    const date = new Date(entry.timestamp);
    // Example: "Mar 1, 12:00"
    return date.toLocaleString();
  });

  const temps = historyData.map((entry) => entry.temperature);

  tempChart.data.labels = labels;
  tempChart.data.datasets[0].data = temps;
  tempChart.update();
}
