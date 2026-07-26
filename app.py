import os
import streamlit as st
from ai_generator import generate_japanese_story
from db_handler import get_deck_stats, get_session_words

st.set_page_config(
    page_title="Step-Reader | i+1 Japanese Reader",
    layout="centered",
)

# --- CUSTOM BLUEBOOK-STYLE CSS ---
st.markdown(
    """
    <style>
    /* Main container styling */
    .block-container {
        max-width: 780px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Japanese Reading Passage Box */
    .passage-box {
        background-color: rgba(137, 180, 250, 0.05);
        border: 1px solid rgba(137, 180, 250, 0.25);
        border-left: 4px solid #89b4fa;
        border-radius: 8px;
        padding: 24px;
        font-size: 22px;
        line-height: 2.1;
        margin-bottom: 24px;
    }

    /* Target Word Info Cards */
    .target-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
    .target-card .label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.7;
        margin-bottom: 4px;
    }
    .target-card .value {
        font-size: 20px;
        font-weight: 600;
    }

    /* Streamlit Radio Override for Bluebook Look */
    div[data-testid="stRadio"] > label {
        display: none;
    }
    div[data-testid="stRadio"] > div {
        gap: 10px;
    }
    div[data-testid="stRadio"] > div > label {
        display: flex;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        padding: 14px 18px;
        cursor: pointer;
        transition: all 0.15s ease-in-out;
    }
    div[data-testid="stRadio"] > div > label:hover {
        border-color: #89b4fa;
        background-color: rgba(137, 180, 250, 0.04);
    }
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        border-color: #89b4fa;
        background-color: rgba(137, 180, 250, 0.1);
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- HEADER ---
st.title("Step-Reader")
st.caption("Adaptive i+1 Japanese Reading & Comprehension")

# --- SIDEBAR: DECK STATS ---
st.sidebar.title("Deck Overview")
stats = get_deck_stats()

if stats["total"] > 0:
  st.sidebar.write(f"**Mastered / Known:** {stats['mastered']}")
  st.sidebar.write(f"**Learning Pool (+1):** {stats['learning']}")
  st.sidebar.write(f"**Total Vocabulary:** {stats['total']}")
else:
  st.sidebar.error("words.json file not found or empty.")

st.sidebar.markdown("---")
st.sidebar.caption("Source: words.json")

st.markdown("---")

# --- GENERATE BUTTON ---
if st.button(
    "Generate Passage & Question", type="primary", use_container_width=True
):
  with st.spinner("Preparing reading passage..."):
    target, context, msg = get_session_words(num_context=15)

    if not target:
      st.error(f"Error: {msg}")
    else:
      story_data = generate_japanese_story(target, context)

      if story_data and "error" not in story_data:
        st.session_state["current_story"] = story_data
        st.session_state["current_target"] = target
        st.session_state["quiz_submitted"] = False
        st.session_state["user_choice_index"] = 0
        st.rerun()
      else:
        err_msg = (
            story_data.get("error", "Failed to generate passage.")
            if story_data
            else "Failed to generate passage."
        )
        st.error(err_msg)

# --- RENDER PASSAGE & QUESTION IF GENERATED ---
if "current_story" in st.session_state:
  story = st.session_state["current_story"]
  target = st.session_state["current_target"]

  st.write("")

  # Target Word Bar
  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        f'<div class="target-card"><div class="label">Target'
        f' Kanji</div><div class="value">{target["kanji"]}</div></div>',
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        f'<div class="target-card"><div class="label">Reading</div><div'
        f' class="value">{target["reading"]}</div></div>',
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        f'<div class="target-card"><div class="label">Meaning</div><div'
        f' class="value">{target["meaning"]}</div></div>',
        unsafe_allow_html=True,
    )

  st.write("")

  # Passage Header & Box
  title = story.get("title", "Reading Practice")
  st.subheader(title)

  st.markdown(
      f'<div class="passage-box">{story.get("story_japanese", "")}</div>',
      unsafe_allow_html=True,
  )

  with st.expander("Translation & Grammar Context"):
    st.markdown(f"**English Translation:** {story.get('story_english', '')}")
    st.markdown(f"**Grammar Note:** {story.get('grammar_note', '')}")

  st.markdown("---")

  # Question & Choice Section (Bluebook Style)
  st.subheader("Comprehension Question")

  q_jp = story.get("question_japanese", "")
  q_en = story.get("question_english", "")
  options = story.get("options", [])
  correct_idx = int(story.get("correct_index", 0))

  st.markdown(f"**{q_jp}**")
  if q_en:
    with st.expander("Show Question Translation"):
      st.caption(q_en)

  st.write("")

  if options and len(options) == 4:
    labels = ["A", "B", "C", "D"]

    # Radio options styled as clean cards
    selected_option_idx = st.radio(
        "Select your answer:",
        options=range(4),
        format_func=lambda i: f"{labels[i]}.   {options[i]}",
        key="quiz_radio",
    )

    st.write("")

    col_btn, _ = st.columns([1, 2])
    with col_btn:
      if st.button(
          "Submit Answer", type="secondary", use_container_width=True
      ):
        st.session_state["quiz_submitted"] = True
        st.session_state["user_choice_index"] = selected_option_idx

    if st.session_state.get("quiz_submitted", False):
      user_idx = st.session_state.get("user_choice_index", 0)
      st.write("")

      if user_idx == correct_idx:
        st.success(
            f"Correct. Option {labels[correct_idx]} is the right answer."
        )
      else:
        st.error(
            f"Incorrect. You selected Option {labels[user_idx]}, but Option"
            f" {labels[correct_idx]} is correct."
        )

      st.markdown("#### Explanation")
      st.info(f"**[JP]** {story.get('explanation_jp', '')}")

      with st.expander("English Explanation"):
        st.markdown(f"**[EN]** {story.get('explanation_en', '')}")

  st.markdown("---")

  used_words = story.get("words_used", [])
  with st.expander(
      f"Vocabulary Reference ({len(used_words)} context words used)"
  ):
    if used_words:
      for word in used_words:
        st.write(
            f"• **{word.get('kanji', '')}** ({word.get('reading', '')}) —"
            f" {word.get('meaning', '')}"
        )
    else:
      st.caption("No additional vocabulary referenced.")

else:
  st.info("Select 'Generate Passage & Question' above to begin your session.")