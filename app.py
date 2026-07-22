from flask import Flask, render_template

app = Flask(__name__)

# ---------------- Home ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- Faculty Login ----------------
@app.route("/faculty-login")
def faculty_login():
    return render_template("faculty_login.html")


# ---------------- Student Login ----------------
@app.route("/student-login")
def student_login():
    return render_template("student_login.html")


# ---------------- Faculty Dashboard ----------------
@app.route("/faculty-dashboard")
def faculty_dashboard():
    return render_template("faculty_dashboard.html")


# ---------------- Student Dashboard ----------------
@app.route("/student-dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")


# ---------------- Upload Page ----------------
@app.route("/upload")
def upload():
    return render_template("upload.html")


# ---------------- Result Page ----------------
@app.route("/result")
def result():
    return render_template("result.html")


# ---------------- Transcript Page ----------------
@app.route("/transcript")
def transcript():
    return render_template("transcript.html")
@app.route("/admin-login")
def admin_login():
    return render_template("admin_login.html")
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)