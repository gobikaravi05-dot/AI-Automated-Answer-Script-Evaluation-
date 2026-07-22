import os
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def summarize_text(text):
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=f"Summarize the following text:\n\n{text}"
    )
    return response.text