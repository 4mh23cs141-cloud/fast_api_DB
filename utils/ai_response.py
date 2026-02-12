import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("VITE_GEMINI_API_KEY")

if not api_key:
    api_key = "AIzaSyAJxAfPN4x-qtiVFKIso30r4X-JOz3IiQs"

genai.configure(api_key=api_key)

model = genai.GenerativeModel('models/gemini-2.5-flash')

def get_completion(user_message, system_message="You are Nexus AI, a premium intelligent assistant."):
    """
    Get a completion from the Gemini model on the backend.
    """
    try:
        full_prompt = f"{system_message}\n\nUser: {user_message}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Backend Error: {e}")
        return f"System Error: {str(e)}"
