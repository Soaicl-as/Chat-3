from flask import Flask, request, render_template_string, session
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired
import time

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Replace with a strong secret in production

client = Client()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            # Attempt login
            client.login(username, password)
            return "✅ Logged in successfully!"

        except ChallengeRequired as e:
            # Instagram flagged the login as suspicious (ChallengeRequired)
            print("⚠️ Challenge required. Waiting for you to confirm login in the Instagram app...")
            
            # Save the challenge identifier for further steps
            session["challenge_id"] = e.challenge.id
            print(f"Challenge ID: {session['challenge_id']}")

            # Instruct user to approve login manually
            return """
                <h2>Instagram Login</h2>
                <p>Instagram has flagged this login attempt as suspicious. Please confirm that it's you in the Instagram app/website.</p>
                <p>Once you approve, the bot will automatically retry to log you in.</p>
                <form method="post">
                    <input type="submit" value="Retry Login" />
                </form>
            """

        except TwoFactorRequired:
            # Instagram is asking for 2FA (e.g., via SMS)
            print("⚠️ Two-factor authentication is required.")
            return """
                <h2>Instagram Login</h2>
                <p>Instagram requires 2FA. Please complete the 2FA challenge.</p>
                <form method="post">
                    <input type="text" name="verification_code" placeholder="Enter your 2FA code" required><br><br>
                    <input type="submit" value="Submit">
                </form>
            """

        except Exception as e:
            return f"❌ Login failed: {str(e)}", 500

    # Page for first-time login
    return render_template_string('''
        <!doctype html>
        <html>
            <head><title>Instagram Login</title></head>
            <body>
                <h2>Instagram Login</h2>
                <form method="post">
                    <label>Username:</label><br>
                    <input type="text" name="username" required><br><br>
                    <label>Password:</label><br>
                    <input type="password" name="password" required><br><br>
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
    ''')

@app.route("/retry-login", methods=["POST"])
def retry_login():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        # Retry login after challenge approval
        if "challenge_id" in session:
            # Instagram Challenge has been cleared by the user
            print("✅ Challenge cleared. Retrying login...")
            client.login(username, password)
            return "✅ Logged in successfully after confirmation!"

        return "❌ No challenge detected. Please try again later."

    except Exception as e:
        return f"❌ Login failed during retry: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
