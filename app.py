from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = "swiftflux_secret"

DATA_FILE = os.path.join("data", "users.json")

def read_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = read_users()
        user = users.get(email)
        if user and user["password"] == password:
            session["user"] = email
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = read_users()
        if email in users:
            return render_template("signup.html", error="User already exists")
        users[email] = {"password": password, "balance": 1000.0, "transactions": []}
        write_users(users)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    email = session["user"]
    users = read_users()
    user = users.get(email, {})
    message = ""
    if request.method == "POST":
        amount = float(request.form["amount"])
        action = request.form["action"]
        if action == "Deposit":
            user["balance"] += amount
            user["transactions"].append(f"Deposited ${amount}")
        elif action == "Withdraw":
            if user["balance"] >= amount:
                user["balance"] -= amount
                user["transactions"].append(f"Withdrew ${amount}")
            else:
                message = "Insufficient funds"
        users[email] = user
        write_users(users)
    return render_template("dashboard.html", balance=user["balance"], transactions=user["transactions"], message=message)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
