from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint("auth", __name__)

FACULTY_EMAIL = "admin@siet.com"
FACULTY_PASSWORD = "admin123"


@auth_bp.route("/faculty-login", methods=["GET", "POST"])
def faculty_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == FACULTY_EMAIL and password == FACULTY_PASSWORD:
            return redirect(url_for("faculty_dashboard"))

        return "Invalid Email or Password"

    return render_template("faculty_login.html")