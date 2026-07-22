from flask import Flask, render_template
from database.models import create_tables
from routes.upload import upload_bp
from routes.evaluate import evaluate_bp

# Create Flask App
app = Flask(__name__)

# Create Database Tables
create_tables()

# Register API Routes
app.register_blueprint(upload_bp)
app.register_blueprint(evaluate_bp)


# -----------------------------
# FRONTEND ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/faculty-login")
def faculty_login():
    return render_template("faculty_login.html")


@app.route("/student-login")
def student_login():
    return render_template("student_login.html")


@app.route("/faculty-dashboard")
def faculty_dashboard():
    return render_template("faculty_dashboard.html")


@app.route("/student-dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)