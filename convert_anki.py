import json
import os

anki_file = "anki_export.txt"
output_file = "words.json"

if not os.path.exists(anki_file):
    print(f"Error: Could not find '{anki_file}'. Please place your exported text file in this project folder!")
    exit(1)

words_list = []

with open(anki_file, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, start=1):
        cleaned_line = line.strip()
        if not cleaned_line or cleaned_line.startswith("#"):
            continue
        
        parts = cleaned_line.split("\t")
        
        # We need at least 4 columns based on your deck structure
        if len(parts) >= 4:
            kanji = parts[0].strip()
            # parts[1] is Kanji + furigana (we can skip it)
            reading = parts[2].strip()  # ひとつ
            meaning = parts[3].strip()  # one (thing)
            
            status = "mastered" if idx <= 25 else "learning"
            
            word_entry = {
                "id": idx,
                "kanji": kanji,
                "reading": reading,
                "meaning": meaning,
                "status": status,
                "jlpt_level": "N5"
            }
            words_list.append(word_entry)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(words_list, f, ensure_ascii=False, indent=2)

print(f"✅ Success! Converted {len(words_list)} words into '{output_file}'.")