// signin.js
const SERVER_URL = "http://<RASPBERRY_PI_IP>:5000";

document.addEventListener("DOMContentLoaded", () => {
  const googleSignInBtn = document.getElementById("googleSignInBtn");

  googleSignInBtn.addEventListener("click", () => {
    // Redirect to the server route that handles Google OAuth sign-in
    window.location.href = `${SERVER_URL}/auth/google/signin`;
  });
});
