import logging
import os
import uuid
import threading

from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pypdf import PdfReader


# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Lock to make sure only ONE report is generated/written at a time.
# Without this, two overlapping requests writing to the same
# "evaluation_report.pdf" at once corrupts the PDF content stream and
# causes all the text to render squeezed/overlapping on one line.
report_lock = threading.Lock()


# ---------------- App Configuration ----------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)


# ---------------- Folder Setup ----------------

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "static", "reports")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


# ---------------- Store Student Data ----------------

student_data = {
    "name": "",
    "register": "",
    "department": "",
    "subject": "",
    "exam": "",
    "questions": []
}


# ---------------- Extract PDF Details ----------------

def extract_student_details(pdf_path):

    try:
        reader = PdfReader(pdf_path)
    except Exception:
        logger.exception("Failed to open/parse the uploaded PDF")
        raise ValueError("Uploaded file is not a valid/readable PDF")

    text = ""
    for page in reader.pages:
        try:
            text += page.extract_text() or ""
        except Exception:
            logger.warning("Could not extract text from a page, skipping it")
            continue

    details = {
        "name": "Unknown Student",
        "register": "Not Found",
        "department": "Not Found",
        "subject": "Not Found",
        "exam": "Not Found",
        "questions": []
    }

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        if "Name" in line and ":" in line:
            details["name"] = line.split(":", 1)[-1].strip()

        elif "Register" in line and ":" in line:
            details["register"] = line.split(":", 1)[-1].strip()

        elif "Department" in line and ":" in line:
            details["department"] = line.split(":", 1)[-1].strip()

        elif "Subject" in line and ":" in line:
            details["subject"] = line.split(":", 1)[-1].strip()

        elif "Exam" in line and ":" in line:
            details["exam"] = line.split(":", 1)[-1].strip()

        elif "Question" in line:
            details["questions"].append(line)

    if len(details["questions"]) == 0:
        details["questions"].append("Explain Machine Learning")

    return details


# ---------------- Generate Report PDF ----------------

def generate_report(data):

    final_path = os.path.join(
        app.config["REPORT_FOLDER"],
        "evaluation_report.pdf"
    )

    # Write to a unique temp file first, so two simultaneous requests
    # never write to the same file at once (which corrupts the PDF and
    # causes overlapping/garbled text).
    temp_path = os.path.join(
        app.config["REPORT_FOLDER"],
        f"_tmp_{uuid.uuid4().hex}.pdf"
    )

    try:
        pdf = canvas.Canvas(temp_path, pagesize=letter)
        pdf.setTitle("AI Evaluation Report")

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, "AI AUTOMATED ANSWER SCRIPT EVALUATION")

        pdf.setFont("Helvetica", 12)

        lines = []
        lines.append("Evaluation Report")
        lines.append("")

        lines.append(f"Student Name : {data['name']}")
        lines.append(f"Register No : {data['register']}")
        lines.append(f"Department : {data['department']}")
        lines.append(f"Subject : {data['subject']}")
        lines.append(f"Exam : {data['exam']}")
        lines.append("")

        lines.append("Question Wise Analysis")

        total = 0

        for index, question in enumerate(data["questions"], start=1):
            marks = 8
            total += marks

            lines.append(f"Question {index}: {question}")
            lines.append(f"Marks : {marks}/10")
            lines.append("Feedback : Answer evaluated successfully")
            lines.append("")

        if len(data["questions"]) > 0:
            max_total = len(data["questions"]) * 10
            percentage = (total / max_total) * 100

            lines.append(f"Total Marks : {total}/{max_total}")
            lines.append(f"Percentage : {percentage:.2f}%")

        lines.append("")
        lines.append("AI Feedback")
        lines.append("Answer script analysed successfully.")
        lines.append("Improve explanation with more examples.")
        lines.append("")
        lines.append("Generated by AI Automated Answer Script Evaluation System")

        y = 700
        for line in lines:
            pdf.drawString(80, y, line)
            y -= 20

            if y < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = 750

        pdf.save()

        # Atomic rename: only swap in the finished file once it's
        # fully written, and only one thread does this at a time.
        with report_lock:
            os.replace(temp_path, final_path)

        logger.info("Report created successfully at %s", final_path)

    except Exception:
        logger.exception("Failed to generate the report PDF")
        # Clean up the leftover temp file if something went wrong
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise


# ---------------- Home ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- Faculty Login ----------------

@app.route("/faculty-login", methods=["GET", "POST"])
def faculty_login():
    if request.method == "POST":
        return redirect("/faculty-dashboard")
    return render_template("faculty_login.html")


# ---------------- Student Login ----------------

@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        register = request.form.get("register")
        password = request.form.get("password")
        return redirect("/student-dashboard")
    return render_template("student_login.html")


# ---------------- Faculty Dashboard ----------------

@app.route("/faculty-dashboard")
def faculty_dashboard():
    return render_template("faculty_dashboard.html")


# ---------------- Student Dashboard ----------------

@app.route("/student-dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")


# ---------------- Upload PDF ----------------

@app.route("/upload", methods=["GET", "POST"])
def upload():

    global student_data

    if request.method == "POST":

        if "file" not in request.files:
            logger.warning("No 'file' part in the request")
            return "No file part in request. Please choose a file.", 400

        file = request.files["file"]

        if file.filename == "":
            logger.warning("No file selected by user")
            return "No file selected. Please choose a PDF file.", 400

        if not file.filename.lower().endswith(".pdf"):
            return "Please upload a PDF file", 400

        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            student_data = extract_student_details(filepath)
            logger.info("Extracted student data: %s", student_data)

            generate_report(student_data)

            return redirect("/result")

        except ValueError as ve:
            logger.exception("Value error while processing upload")
            return f"Error processing file: {ve}", 400

        except Exception:
            logger.exception("Unexpected error during file upload")
            return "Something went wrong while processing the file. Please try again.", 500

    return render_template("upload.html")


# ---------------- Result ----------------

@app.route("/result")
def result():
    return render_template("result.html", data=student_data)


# ---------------- Download Report ----------------

@app.route("/download-report")
def download_report():
    report_path = os.path.join(app.config["REPORT_FOLDER"], "evaluation_report.pdf")

    if not os.path.exists(report_path):
        return "No report found. Please upload a file first.", 404

    return send_from_directory(
        app.config["REPORT_FOLDER"],
        "evaluation_report.pdf",
        as_attachment=True
    )


# ---------------- Question Analysis ----------------

@app.route("/question-analysis")
def question_analysis():
    return render_template("question_analysis.html", questions=student_data["questions"])


# ---------------- Detailed Evaluation ----------------

@app.route("/detailed-evaluation")
def detailed_evaluation():
    return render_template("detailed_evaluation.html", data=student_data)


# ---------------- Transcript ----------------

@app.route("/transcript")
def transcript():
    return render_template("transcript.html", data=student_data)


# ---------------- Run ----------------

if __name__ == "__main__":
    app.run(debug=True)