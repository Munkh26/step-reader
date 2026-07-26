import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def get_client():
  """Safely retrieves the Gemini client or returns None if key is missing."""
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    return None
  return genai.Client(api_key=api_key)


def generate_japanese_story(target_word, context_words):
  """Generates an i+1 Japanese story and quiz using Gemini."""
  client = get_client()

  if not client:
    return {
        "error": (
            "GEMINI_API_KEY is not set. Please set it in your environment or"
            " .env file!"
        )
    }

  context_str = ", ".join(
      [f"{w['kanji']} ({w['reading']})" for w in context_words]
  )

  prompt = f"""
    You are an expert Japanese language tutor creating an i+1 reading comprehension passage.

    TARGET WORD (The +1 new word the student must learn):
    - Kanji: {target_word.get('kanji', '')}
    - Reading: {target_word.get('reading', '')}
    - Meaning: {target_word.get('meaning', '')}

    AVAILABLE KNOWN VOCABULARY (Use ONLY these words plus basic grammar particles like は, が, を, に, で, と, です, ます):
    {context_str}

    RULES:
    1. Write a short, natural Japanese story (2 to 4 sentences).
    2. The story MUST naturally feature the TARGET WORD: {target_word.get('kanji', '')}.
    3. Keep grammar appropriate for beginner/intermediate learners (N5/N4 level).
    4. Create a 4-option multiple choice reading comprehension question about the story in Japanese.

    OUTPUT FORMAT:
    You must return ONLY a JSON object with this exact schema:
    {{
        "title": "Title in Japanese",
        "story_japanese": "Full story in Japanese",
        "story_english": "English translation of story",
        "grammar_note": "A brief 1-sentence note on key grammar used",
        "question_japanese": "Question in Japanese",
        "question_english": "Question translation in English",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_index": 0,
        "explanation_jp": "Explanation in Japanese of why the correct option is right",
        "explanation_en": "Explanation in English of why the correct option is right",
        "words_used": [
            {{"kanji": "...", "reading": "...", "meaning": "..."}}
        ]
    }}
    """

  try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    story_data = json.loads(response.text)
    return story_data

  except json.JSONDecodeError:
    return {"error": "Failed to parse JSON response from Gemini."}
  except Exception as e:
    return {"error": f"API Error: {str(e)}"}