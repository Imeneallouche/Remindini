// dashboard.js

// The URL of your Flask server (running on Raspberry Pi)
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM elements for SMS stats
const smsSuccessCountEl = document.getElementById("smsSuccessCount");

// DOM elements for gauges
const currentTemperatureEl = document.getElementById("currentTemperature");
const currentHumidityEl = document.getElementById("currentHumidity");
const tempThresholdEl = document.getElementById("tempThreshold");
const humidityThresholdEl = document.getElementById("humidityThreshold");
const refreshGaugesBtn = document.getElementById("refreshGaugesBtn");

// Sidebar header element
const sidebarHeader = document.querySelector(".sidebar-header");

// Gauge objects
let tempGauge;
let humidityGauge;

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize gauges
  initGauges();
  
  // 2. Fetch SMS stats
  fetchSmsStats();
  
  // 3. Fetch environmental data (temperature and humidity)
  fetchEnvironmentalData();
  
  // 4. Set up refresh button
  refreshGaugesBtn.addEventListener("click", () => {
    fetchEnvironmentalData();
  });
  
  // 5. Set up auto-refresh interval (every 30 seconds)
  setInterval(fetchEnvironmentalData, 30000);
  
  // 6. Add click event for sidebar header to navigate to dashboard
  sidebarHeader.addEventListener("click", () => {
    window.location.href = "/dashboard";
  });
});

/**
 * Initializes the temperature and humidity gauges using doughnut charts
 */
function initGauges() {
  // Temperature gauge
  const tempCtx = document.getElementById("tempGauge").getContext("2d");
  tempGauge = new Chart(tempCtx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [0, 200],
        backgroundColor: ['#ff7043', '#e0e0e0'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '70%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      }
    }
  });
  
  // Humidity gauge
  const humidityCtx = document.getElementById("humidityGauge").getContext("2d");
  humidityGauge = new Chart(humidityCtx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [0, 100],
        backgroundColor: ['#29b6f6', '#e0e0e0'],
        borderWidth: 0,
        circumference: 180,
        rotation: 270
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '70%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: false
        }
      }
    }
  });
}

/**
 * Fetches the SMS stats (success count) for the current week.
 */
async function fetchSmsStats() {
  try {
    const response = await fetch(`${SERVER_URL}/api/sms-stats?week=current`);
    if (!response.ok) {
      throw new Error(`Error fetching SMS stats: ${response.status}`);
    }
    const data = await response.json();
    smsSuccessCountEl.textContent = `${data.successCount} SMS`;
  } catch (error) {
    console.error(error);
    smsSuccessCountEl.textContent = "-- SMS";
  }
}

/**
 * Fetches environmental data (temperature and humidity) from the server.
 */
async function fetchEnvironmentalData() {
  try {
    const response = await fetch(`${SERVER_URL}/api/environmental-data`);
    if (!response.ok) {
      throw new Error(`Error fetching environmental data: ${response.status}`);
    }
    const data = await response.json();
    
    // Update gauges with received data
    updateTemperatureGauge(data.temperature.current, data.temperature.threshold);
    updateHumidityGauge(data.humidity.current, data.humidity.threshold);
  } catch (error) {
    console.error(error);
    currentTemperatureEl.textContent = "--";
    currentHumidityEl.textContent = "--";
    tempThresholdEl.textContent = "--";
    humidityThresholdEl.textContent = "--";
  }
}

/**
 * Updates the temperature gauge with new values
 * @param {number} current - The current temperature
 * @param {number} threshold - The temperature threshold
 */
function updateTemperatureGauge(current, threshold) {
  // Calculate percentage (0-50°C range is typical for room temperature)
  const maxTemp = 50;
  const percentage = (current / maxTemp) * 100;
  
  // Update gauge value - limit to 100%
  const cappedPercentage = Math.min(percentage, 100);
  tempGauge.data.datasets[0].data = [cappedPercentage, 100 - cappedPercentage];
  tempGauge.update();
  
  // Update text display
  currentTemperatureEl.textContent = current.toFixed(1);
  tempThresholdEl.textContent = threshold.toFixed(1);
  
  // Apply visual indication if temperature exceeds threshold
  if (current > threshold) {
    currentTemperatureEl.parentElement.style.color = '#f44336';
  } else {
    currentTemperatureEl.parentElement.style.color = '#333';
  }
}

/**
 * Updates the humidity gauge with new values
 * @param {number} current - The current humidity
 * @param {number} threshold - The humidity threshold
 */
function updateHumidityGauge(current, threshold) {
  // Calculate percentage (humidity is already 0-100%)
  const percentage = Math.min(current, 100);
  
  // Update gauge value
  humidityGauge.data.datasets[0].data = [percentage, 100 - percentage];
  humidityGauge.update();
  
  // Update text display
  currentHumidityEl.textContent = current.toFixed(1);
  humidityThresholdEl.textContent = threshold.toFixed(1);
  
  // Apply visual indication if humidity exceeds threshold
  if (current > threshold) {
    currentHumidityEl.parentElement.style.color = '#f44336';
  } else {
    currentHumidityEl.parentElement.style.color = '#333';
  }
}