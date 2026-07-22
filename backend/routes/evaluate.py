from flask import Blueprint, request, jsonify
import os

from ai.ocr import extract_text
from ai.evaluator import evaluate_answer

evaluate_bp = Blueprint("evaluate", __name__)

UPLOAD_FOLDER = "uploads"


@evaluate_bp.route("/evaluate", methods=["POST"])
def evaluate():

    try:

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        student_answer = extract_text(filepath)

        question = request.form.get("question")
        answer_key = request.form.get("answer_key")

        # DEBUG
        print("========== DEBUG ==========")
        print("QUESTION:")
        print(question)
        print()

        print("ANSWER KEY:")
        print(answer_key)
        print()

        print("STUDENT ANSWER:")
        print(student_answer)
        print()

        result = evaluate_answer(
            question,
            answer_key,
            student_answer
        )

        print("GEMINI RESULT:")
        print(result)
        print("===========================")

        return jsonify({
            "student_answer": student_answer,
            "evaluation": result
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "error": str(e)
        }), 500