from ai.transcript import summarize_text

text = """
Hands on Session on IMAGE MODEL TRAINING TO DEPLOYMENT
FastAPI Backend
Dockerization
Streamlit UI
"""

print("===== GEMINI OUTPUT =====")
print(summarize_text(text))