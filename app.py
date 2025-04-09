from flask import Flask, request, render_template_string
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
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
            # First login attempt
            client.login(username, password)
            return "✅ Logged in successfully!"

        except ChallengeRequired:
            # Instagram flagged the login as suspicious (ChallengeRequired)
            print("⚠️ Challenge required. Waiting for you to confirm login in the Instagram app...")

            # Retry until you clear the challenge on Instagram
            max_retries = 10
            for attempt in range(max_retries):
                print(f"Attempt {attempt + 1}/{max_retries}: Waiting for Instagram confirmation...")
                time.sleep(10)

                try:
                    # Retry login after you confirm in Instagram
                    client.login(username, password)
                    return "✅ Logged in after Instagram confirmation!"
                except ChallengeRequired:
                    continue  # Try again if challenge still required
                except Exception as inner_error:
                    return f"❌ Login failed during retry: {str(inner_error)}", 500

            return "❌ Login blocked. You didn’t confirm the login in time. Please try again.", 403

        except Exception as e:
            return f"❌ Login failed: {str(e)}", 500

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

if __name__ == "__main__":
    app.run(debug=True)
