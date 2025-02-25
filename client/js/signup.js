// signup.js

// The URL of your Flask server (running on Raspberry Pi):
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signupForm");
  const googleSignUpBtn = document.getElementById("googleSignUpBtn");

  // Standard form submit (without Google OAuth)
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const firstName = document.getElementById("firstName").value;
    const lastName = document.getElementById("lastName").value;
    const phoneNumber = document.getElementById("phoneNumber").value;

    // Send the data to the Flask server
    try {
      const response = await fetch(`${SERVER_URL}/api/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ firstName, lastName, phoneNumber }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Sign-up successful: ${data.message}`);
        // Possibly redirect to dashboard or sign-in page
        window.location.href = "signin.html";
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (err) {
      console.error("Sign-up error:", err);
      alert("An error occurred. Please try again.");
    }
  });

  // Google sign-up button (example of how you'd start an OAuth flow)
  googleSignUpBtn.addEventListener("click", () => {
    // Typically, you'd redirect to your Flask route that handles Google OAuth
    // or use a client-side Google API script. For instance:
    window.location.href = `${SERVER_URL}/auth/google/signup`;
  });
});
