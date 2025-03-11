from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google_auth_oauthlib.flow import Flow
import os
import json
import requests

GOOGLE_CLIENT_CONFIG_FILE = "config/google_client.json"

# Load Google OAuth2 configuration
with open(GOOGLE_CLIENT_CONFIG_FILE, "r") as config_file:
    GOOGLE_CLIENT_CONFIG = json.load(config_file)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "secret_key"  

BACKEND_URL = "http://192.168.1.37:5000"  


"""To get the user info"""
def get_user_info(access_token):
    """Fetch user info using the access token"""
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(userinfo_url, headers=headers)

    if response.status_code == 200:
        return response.json() 
    else:
        print("Failed to fetch user info:", response.json())
        return None


"""Main route"""
@app.route("/", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        phone_number = request.form["phoneNumber"]
        username = request.form["username"]

        session["phone_number"] = phone_number
        session["username"] = username

        return redirect(url_for("authorize_calendar"))
    return render_template("signup.html")



"""Authorize calendar route"""
@app.route("/authorize_calendar")
def authorize_calendar():
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["openid", "https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/userinfo.email"]
    )
    flow.redirect_uri = url_for("oauth2callback", _external=True)
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)



"""OAuth2 callback route"""
@app.route("/oauth2callback")
def oauth2callback():
    if "state" not in session:
        return redirect(url_for("index"))

    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["openid", "https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/userinfo.email"],
        state=session["state"]
    )
    flow.redirect_uri = url_for("oauth2callback", _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    # Fetch user info from Google API
    user_info = get_user_info(credentials.token)
    if user_info and "email" in user_info:
        session["email"] = user_info["email"]
        print("User email:", session["email"])
    else:
        return jsonify({"error": "Failed to retrieve email"}), 400

    # Ensure refresh_token exists
    # if not credentials.refresh_token:
    #     credentials.refresh_token = session.get("refresh_token", None)

    google_token = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,  
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat(),
    }

    session["google_token"] = google_token
    session["refresh_token"] = google_token["refresh_token"]  

    # Prepare data for saving user
    data = {
        "username": session.get("username"),
        "email": session.get("email"),
        "phone": session.get("phone_number"),
        "google_token": google_token, 
    }

    response = requests.post(f"{BACKEND_URL}/api/save_user", json=data)

    if response.status_code == 200:
        return redirect(url_for("dashboard"))
    elif response.status_code == 409: 
        return redirect(url_for("signup", error="Email already registered. Please sign in."))
    else:
        return jsonify({"error": "Error registering user on server", "details": response.text}), 400



""""Sign in route"""
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



"""Sign in callback route"""
@app.route("/signin/callback")
def signin_callback():
    if "state" not in session:
        return redirect(url_for("signup"))

    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        state=session["state"]
    )
    flow.redirect_uri = url_for("signin_callback", _external=True)
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    # Fetch user info from Google API
    user_info = get_user_info(credentials.token)
    if user_info and "email" in user_info:
        session["email"] = user_info["email"]
        session["google_token"] = credentials.token  
    else:
        return jsonify({"error": "Failed to retrieve email"}), 400

    # Send email to backend for verification
    response = requests.post(f"{BACKEND_URL}/api/signin_user", json={"email": session["email"]})

    if response.status_code == 200:
        data = response.json()
        session["username"] = data["username"]
        session["phone_number"] = data["phone_number"]
        return redirect(url_for("dashboard"))
    elif response.status_code == 403:
        return redirect(url_for("signup", error="You don't have an account with this email. Please sign up first."))
    


"""Logout route"""
@app.route("/signout")
def signout():
    session.clear() 
    return redirect(url_for("signup"))  



"""Dashboard route"""
@app.route("/dashboard")
def dashboard():
    if "google_token" not in session:
        return redirect(url_for("signup"))
    return render_template("dashboard.html", username=session.get("username"))



@app.route("/settings")
def settings():
    if "google_token" not in session:
        return redirect(url_for("signup"))
    return render_template("settings.html", username=session.get("username"), phone_number=session.get("phone_number"))



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)