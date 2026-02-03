"""Quick test to check available Gemini models"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API key found!")
else:
    print(f"API Key found: {api_key[:10]}...")
    
    genai.configure(api_key=api_key)
    
    print("\nAvailable models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
