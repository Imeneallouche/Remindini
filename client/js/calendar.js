// calendar.js

const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

// DOM elements
const reminderValueInput = document.getElementById("reminderValue");
const reminderUnitSelect = document.getElementById("reminderUnit");
const updateReminderBtn = document.getElementById("updateReminderBtn");
const calendarGrid = document.getElementById("calendarGrid");

document.addEventListener("DOMContentLoaded", () => {
  // 1. Fetch and display calendar events
  fetchCalendarEvents();

  // 2. Handle update reminder button
  updateReminderBtn.addEventListener("click", () => {
    const reminderValue = parseInt(reminderValueInput.value, 10);
    const reminderUnit = reminderUnitSelect.value;
    updateReminder(reminderValue, reminderUnit);
  });
});

/**
 * Fetch calendar events from the server and render them.
 */
async function fetchCalendarEvents() {
  try {
    const response = await fetch(`${SERVER_URL}/api/calendar-events`);
    if (!response.ok) {
      throw new Error(`Error fetching calendar events: ${response.status}`);
    }
    const data = await response.json();
    // data might be an array of events like:
    // [
    //   { summary: "Event 1", start: "2025-02-25T09:00:00", end: "2025-02-25T10:00:00" },
    //   { summary: "Event 2", start: "2025-02-25T13:00:00", end: "2025-02-25T14:30:00" },
    //   ...
    // ]
    renderCalendar(data);
  } catch (error) {
    console.error(error);
  }
}

/**
 * Renders the events in the calendar grid.
 * This is a simplified approach. In reality, you'd parse dates, handle weeks, etc.
 */
function renderCalendar(events) {
  // Clear the grid first
  calendarGrid.innerHTML = "";

  // Create 35 cells (5 rows x 7 columns) for the prototype
  for (let i = 0; i < 35; i++) {
    const dayCell = document.createElement("div");
    dayCell.classList.add("day-cell");

    // Filter events for a hypothetical day range if needed
    // For now, let's just randomly place them as a placeholder
    // In a real scenario, you'd match event date to cell date
    const dayEvents = events.filter(() => Math.random() < 0.1);
    // This random approach is purely for demonstration.

    dayEvents.forEach((event) => {
      const eventBlock = document.createElement("div");
      eventBlock.classList.add("event-block");
      eventBlock.textContent = event.summary;
      dayCell.appendChild(eventBlock);
    });

    calendarGrid.appendChild(dayCell);
  }
}

/**
 * Updates the reminder setting on the server.
 * E.g., the user wants reminders 2 hours before the event.
 */
async function updateReminder(value, unit) {
  try {
    const response = await fetch(`${SERVER_URL}/api/reminder-settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value, unit }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      alert(`Failed to update reminder: ${errorData.message}`);
      return;
    }
    const data = await response.json();
    alert(`Reminder updated: ${data.message}`);
  } catch (error) {
    console.error("Error updating reminder:", error);
  }
}
