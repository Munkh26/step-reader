import json
import os
import random

WORDS_FILE = "words.json"


def load_words():
  """Reads vocabulary from words.json."""
  if not os.path.exists(WORDS_FILE):
    return None
  with open(WORDS_FILE, "r", encoding="utf-8") as f:
    return json.load(f)


def get_deck_stats():
  """Returns current word counts for display in the sidebar UI."""
  words = load_words()
  if not words:
    return {"total": 0, "mastered": 0, "learning": 0}

  mastered = sum(
      1 for w in words if w.get("status") in ["mastered", "learned"]
  )
  learning = sum(1 for w in words if w.get("status") == "learning")
  return {"total": len(words), "mastered": mastered, "learning": learning}


def get_session_words(num_context=15):
  """Selects 1 target word from 'learning' and samples context words

  strictly from 'mastered' or 'learned' words.
  """
  words = load_words()

  if not words:
    return (
        None,
        None,
        (
            f"Could not find '{WORDS_FILE}'. Please verify the file exists in"
            " your workspace!"
        ),
    )

  learning_words = [w for w in words if w.get("status") == "learning"]
  mastered_words = [
      w for w in words if w.get("status") in ["mastered", "learned"]
  ]

  if not learning_words:
    return None, None, "No 'learning' status words found in your words.json!"

  if not mastered_words:
    return (
        None,
        None,
        "No 'mastered' or 'learned' status words found in your words.json!",
    )

  target_word = random.choice(learning_words)
  sample_size = min(len(mastered_words), num_context)
  context_words = random.sample(mastered_words, sample_size)

  return target_word, context_words, "Success"