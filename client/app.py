from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google_auth_oauthlib.flow import Flow
import os
import json
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as requests_google

GOOGLE_CLIENT_CONFIG_FILE = "config/google_client.json"

# Load Google OAuth2 configuration
with open(GOOGLE_CLIENT_CONFIG_FILE, "r") as config_file:
    GOOGLE_CLIENT_CONFIG = json.load(config_file)

# Allow OAuth in local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "secret_key"  # Replace with a real secret key

BACKEND_URL = "http://192.168.43.38:5000"  # Server URL

@app.route("/")
def index():
    return render_template("signup.html")

@app.route("/signup", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        phoneNumber = request.form["phoneNumber"]
        username = request.form["username"]

        session["phoneNumber"] = phoneNumber
        session["username"] = username

        return redirect(url_for("authorize_calendar"))
    return render_template("signup.html")

@app.route("/authorize_calendar")
def authorize_calendar():
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["https://www.googleapis.com/auth/calendar.readonly","openid", "https://www.googleapis.com/auth/userinfo.email"]
    )
    flow.redirect_uri = url_for("oauth2callback", _external=True)
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    if "state" not in session:
        return redirect(url_for("index"))
    
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["https://www.googleapis.com/auth/calendar.readonly","openid", "https://www.googleapis.com/auth/userinfo.email"],
        state=session["state"]
    )
    flow.redirect_uri = url_for("oauth2callback", _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    google_token = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat(),
    }
    

    # Vérifiez si credentials.id_token est bien un JWT encodé
    if isinstance(credentials.id_token, str):
        try:
            decoded_token = id_token.verify_oauth2_token(credentials.id_token, requests_google.Request())
            session["email"] = decoded_token['email']
            print(session["email"])
        except ValueError as e:
            print("Erreur de validation du token :", e)
    else:
        session["email"] = credentials.id_token.get('email')  # Si déjà un dict
    
    session["google_token"] = credentials.token
    
    data = {
        "username": session.get("username"),
        "email": session.get("email"),
        "phone": session.get("phoneNumber"),
        "google_token": google_token
    }
    
    response = requests.post(f"{BACKEND_URL}/api/save_user", json=data)
    
    if response.status_code == 200:
        return redirect(url_for("dashboard"))
    else:
        return jsonify({"error": "Error registering user on server"}), 400


@app.route("/signin")
def signin():
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"]
    )
    flow.redirect_uri = url_for("signin_callback", _external=True)
    authorization_url, state = flow.authorization_url(prompt="select_account")
    session["state"] = state
    return redirect(authorization_url)


@app.route("/signin/callback")
def signin_callback():
    if "state" not in session:
        return redirect(url_for("index"))

    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        state=session["state"]
    )
    flow.redirect_uri = url_for("signin_callback", _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    token_info = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    if isinstance(credentials.id_token, str):
        try:
            decoded_token = id_token.verify_oauth2_token(
                credentials.id_token, 
                requests_google.Request(),
                clock_skew_in_seconds=60
                )
            session["email"] = decoded_token['email']
            print(session["email"])
        except ValueError as e:
            print("Erreur de validation du token :", e)
    else:
        session["email"] = credentials.id_token.get('email')

    # Send token to the backend to verify and fetch user info
    response = requests.post(f"{BACKEND_URL}/api/signin_user", json={"email": session["email"]})

    if response.status_code == 200:
        user_data = response.json()
        session["email"] = user_data["email"]
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("signin_failed"))

@app.route("/signin_failed")
def signin_failed():
    return render_template("signin_failed.html")

@app.route("/dashboard")
def dashboard():
    if "google_token" not in session:
        return redirect(url_for("index"))
    return render_template("dashboard.html", username=session.get("username"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
