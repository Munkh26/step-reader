import os
from dotenv import load_dotenv
from google import genai

# 1. Load the environment variables BEFORE creating the client
load_dotenv()

# 2. Get the key from .env explicitly
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set! Check your .env file.")

# 3. Pass the key to the Client
client = genai.Client(api_key=api_key)

# 4. Make the test call
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say 'Hello! Your Gemini API key is working correctly.' in Japanese with an English translation.",
)

print(response.text)