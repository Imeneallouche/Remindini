// edge.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM Elements
const currentTemperatureEl = document.getElementById("currentTemperature");
const durationValueInput = document.getElementById("durationValue");
const durationUnitSelect = document.getElementById("durationUnit");
const updateDurationBtn = document.getElementById("updateDurationBtn");

// Chart.js global reference
let tempChart;

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize the chart
  initChart();

  // 2. Fetch the initial historical data (default 1 week)
  fetchTemperatureHistory();

  // 3. Fetch real-time temperature
  fetchCurrentTemperature();
  // Update the real-time temperature every 5 seconds
  setInterval(fetchCurrentTemperature, 5000);

  // 4. Handle update button for history
  updateDurationBtn.addEventListener("click", () => {
    fetchTemperatureHistory();
  });
});

/**
 * Initializes the Chart.js line chart
 */
function initChart() {
  const ctx = document.getElementById("tempChart").getContext("2d");
  tempChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [], // We'll populate this dynamically
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
 * Fetch the real-time temperature from the server
 */
async function fetchCurrentTemperature() {
  try {
    const response = await fetch(`${SERVER_URL}/api/current-temperature`);
    if (!response.ok) {
      throw new Error(`Error fetching current temperature: ${response.status}`);
    }
    const data = await response.json();
    // data = { temperature: 26 }
    currentTemperatureEl.textContent = `${data.temperature}°C`;
  } catch (error) {
    console.error(error);
  }
}

/**
 * Fetch the historical temperature data based on the selected duration
 */
async function fetchTemperatureHistory() {
  const value = parseInt(durationValueInput.value, 10);
  const unit = durationUnitSelect.value;
  try {
    // Example: GET /api/temperature-history?value=1&unit=week
    const response = await fetch(
      `${SERVER_URL}/api/temperature-history?value=${value}&unit=${unit}`
    );
    if (!response.ok) {
      throw new Error(`Error fetching temperature history: ${response.status}`);
    }
    const data = await response.json();
    // Suppose data is an array of objects: [{ timestamp: "2025-03-01T12:00:00", temperature: 25.5 }, ...]
    updateChart(data);
  } catch (error) {
    console.error(error);
  }
}

/**
 * Update the Chart.js dataset with the fetched historical data
 */
function updateChart(historyData) {
  // Sort data by timestamp, if not already
  historyData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  // Prepare arrays for labels (times) and data (temperatures)
  const labels = historyData.map((entry) => {
    // Format time for display (e.g., "Mar 1, 12:00")
    const date = new Date(entry.timestamp);
    return date.toLocaleString(); // or a custom format
  });

  const temps = historyData.map((entry) => entry.temperature);

  // Update the chart
  tempChart.data.labels = labels;
  tempChart.data.datasets[0].data = temps;
  tempChart.update();
}
