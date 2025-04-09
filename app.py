import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
import time
import threading
from utils import send_mass_dm

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Instagram client setup
client = Client()

# Store session to prevent multiple logins
session_data = {}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        try:
            client.login(username, password)
            session_data['user'] = username
            session_data['client'] = client

            # If login is successful, proceed to dashboard
            return redirect(url_for("dashboard"))
        except TwoFactorRequired as e:
            # Store the two-factor identifier so we can complete it later
            session["two_factor_identifier"] = e.two_factor_identifier
            return redirect(url_for("verify_2fa"))
        except Exception as e:
            flash(f"Login failed: {str(e)}")
            return redirect(url_for("login"))
    
    return render_template("login.html")

@app.route("/verify_2fa", methods=["GET", "POST"])
def verify_2fa():
    if request.method == "POST":
        verification_code = request.form.get("verification_code")
        two_factor_identifier = session.get("two_factor_identifier")

        if two_factor_identifier:
            try:
                # Try completing the 2FA with the verification code
                client.complete_two_factor_login(two_factor_identifier, verification_code)
                session_data['client'] = client  # Store the successful client

                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Error completing 2FA: {str(e)}")
    
    return render_template("verify_2fa.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        target_account = request.form.get("target_account")
        message = request.form.get("message")
        time_delay = int(request.form.get("time_delay"))
        is_followers = request.form.get("target_type") == "followers"

        # Start the mass DM process in a separate thread
        threading.Thread(target=send_mass_dm, args=(target_account, message, time_delay, is_followers)).start()
        
        flash(f"Messages are being sent to {target_account}'s {'followers' if is_followers else 'following'}!")
        return redirect(url_for("dashboard"))
    
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
