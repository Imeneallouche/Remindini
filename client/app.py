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

BACKEND_URL = "http://127.0.0.1:5000"  


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
        # Store all user attributes in session
        data = response.json()
        # Store all user attributes in session
        session["id"] = data.get("id")
        session["username"] = data.get("username")
        session["phone_number"] = data.get("phone_number")
        session["sms_service_activated"] = data.get("sms_service_activated")
        session["temperature_service_activate"] = data.get("temperature_service_activate")
        session["humidity_service_activate"] = data.get("humidity_service_activate")
        session["temperature_treshold"] = data.get("temperature_treshold")
        session["humidity_treshold"] = data.get("humidity_treshold")
        session["reminder_delay"] = data.get("reminder_delay")
        session["reminder_unit"] = data.get("reminder_unit")

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

        # Store all user attributes in session
        session["id"] = data.get("id")
        session["username"] = data.get("username")
        session["phone_number"] = data.get("phone_number")
        session["sms_service_activated"] = data.get("sms_service_activated")
        session["temperature_service_activate"] = data.get("temperature_service_activate")
        session["humidity_service_activate"] = data.get("humidity_service_activate")
        session["temperature_treshold"] = data.get("temperature_treshold")
        session["humidity_treshold"] = data.get("humidity_treshold")
        session["reminder_delay"] = data.get("reminder_delay")
        session["reminder_unit"] = data.get("reminder_unit")
        
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
    return render_template("dashboard.html", 
                           id=session.get("id"),
                           username=session.get("username"), 
                           phone_number=session.get("phone_number"),
                           email=session.get("email"),
                           sms_service_activated=session.get("sms_service_activated"),
                           temperature_service_activate=session.get("temperature_service_activate"),
                           humidity_service_activate=session.get("humidity_service_activate"),
                           temperature_treshold=session.get("temperature_treshold"),
                           humidity_treshold=session.get("humidity_treshold"),
                           reminder_delay=session.get("reminder_delay"),
                           reminder_unit=session.get("reminder_unit"))



@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "google_token" not in session:
        return redirect(url_for("signup"))

    user_id = session.get("id")

    if request.method == "POST":
        data = request.get_json()

        phone_number = data.get("phone_number")
        sms_service_activated = data.get("sms_service_activated")
        reminder_value = data.get("reminder_value")
        reminder_unit = data.get("reminder_unit")

        payload = {}
        if phone_number:
            payload["phone_number"] = phone_number
        if sms_service_activated is not None:
            payload["sms_service_activated"] = sms_service_activated
        if reminder_value is not None and reminder_unit is not None:
            payload["reminder_value"] = int(reminder_value)
            payload["reminder_unit"] = reminder_unit
        if "temperature_service_activate" in data:
            payload["temperature_service_activate"] = data["temperature_service_activate"]
        if "humidity_service_activate" in data:
            payload["humidity_service_activate"] = data["humidity_service_activate"]
        if "temperature_treshold" in data:
            payload["temperature_treshold"] = float(data["temperature_treshold"])
        if "humidity_treshold" in data:
            payload["humidity_treshold"] = float(data["humidity_treshold"])


        response = requests.put(f"{BACKEND_URL}/api/update_user/{user_id}", json=payload)
        if response.status_code == 200:
            updated_data = response.json()
            print("Updated data:", updated_data)
            session.update(updated_data)  # Sync session with updated data
            return jsonify({"success": True, **updated_data}), 200

        return jsonify({"success": False}), 400

    return render_template("settings.html", **session)






if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)