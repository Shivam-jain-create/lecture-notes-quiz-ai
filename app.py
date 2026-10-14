import traceback

import streamlit as st

from chunker import chunk_text, clean_text
from extractor import extract_text_from_pdf, extract_text_from_youtube
from llm_chain import generate_quiz, summarize_text
from quiz import score_quiz, shuffle_quiz

MAX_PDF_MB = 25

st.set_page_config(page_title="Lecture Notes & Quiz AI", page_icon="📚", layout="wide")
st.title("📚 Lecture Notes Summarizer + Quiz Generator")
st.caption("Upload a lecture PDF or paste a YouTube link. Get study notes and a practice quiz.")


def reset_quiz_widgets():
    """Forget old radio-button answers when a new quiz is generated."""
    for k in list(st.session_state.keys()):
        if k.startswith("q_"):
            del st.session_state[k]


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Settings")
    source = st.radio("Input type", ["PDF", "YouTube link"])
    language = st.selectbox("Output language", ["English", "Hindi", "Hinglish"])
    num_questions = st.slider("Number of quiz questions", 3, 10, 5)
    max_chunks = st.slider(
        "Max chunks to process", 3, 30, 10,
        help="Each chunk = 1 API call. Keep this low to stay inside the free-tier limits.",
    )

# ---------------- Input ----------------
uploaded, url = None, ""
if source == "PDF":
    uploaded = st.file_uploader("Upload a lecture PDF", type=["pdf"])
else:
    url = st.text_input("YouTube video link")

# ---------------- Generate ----------------
if st.button("Generate notes & quiz", type="primary"):
    try:
        with st.spinner("Reading your material..."):
            if source == "PDF":
                if uploaded is None:
                    raise ValueError("Please upload a PDF first.")
                data = uploaded.getvalue()
                if len(data) > MAX_PDF_MB * 1024 * 1024:
                    raise ValueError(f"PDF is larger than {MAX_PDF_MB} MB.")
                raw = extract_text_from_pdf(data)
            else:
                if not url.strip():
                    raise ValueError("Please paste a YouTube link first.")
                raw = extract_text_from_youtube(url)
            chunks = chunk_text(clean_text(raw))

        total_chunks = len(chunks)
        chunks = chunks[:max_chunks]

        bar = st.progress(0.0, text="Summarizing...")

        def on_progress(i, n):
            bar.progress(i / n, text=f"Summarizing chunk {i}/{n}")

        notes = summarize_text(chunks, language=language, progress=on_progress)

        bar.progress(1.0, text="Creating quiz...")
        quiz_obj = shuffle_quiz(generate_quiz(notes, num_questions, language))
        bar.empty()

        info = ""
        if total_chunks > max_chunks:
            info = (f"Your material has {total_chunks} chunks; only the first {max_chunks} were used. "
                    "Increase 'Max chunks' in the sidebar to cover more (uses more API quota).")

        reset_quiz_widgets()
        st.session_state.update(notes=notes, quiz=quiz_obj, result=None, info=info)

    except ValueError as e:
        st.error(str(e))
    except Exception:
        traceback.print_exc()  # full error goes to the terminal, not to the user
        st.error("The AI service failed. Please wait a minute and try again.")

# ---------------- Results ----------------
if "notes" in st.session_state:
    tab_notes, tab_quiz = st.tabs(["📝 Notes", "❓ Quiz"])

    with tab_notes:
        if st.session_state.get("info"):
            st.info(st.session_state["info"])
        st.markdown(st.session_state["notes"])
        st.download_button("Download notes (.md)", st.session_state["notes"], file_name="notes.md")

    with tab_quiz:
        quiz_obj = st.session_state["quiz"]
        with st.form("quiz_form"):
            answers = {}
            for i, q in enumerate(quiz_obj.questions):
                answers[i] = st.radio(
                    f"**Q{i + 1}. {q.question}**",
                    options=[0, 1, 2, 3],
                    format_func=lambda j, q=q: f"{'ABCD'[j]}. {q.options[j]}",
                    index=None,
                    key=f"q_{i}",
                )
            submitted = st.form_submit_button("Submit quiz")

        if submitted:
            st.session_state["result"] = score_quiz(quiz_obj, answers)

        result = st.session_state.get("result")
        if result:
            st.subheader(f"Score: {result['score']}/{result['total']} ({result['percent']}%)")
            for i, r in enumerate(result["review"], start=1):
                icon = "✅" if r["is_correct"] else "❌"
                with st.expander(f"{icon} Q{i}. {r['question']}"):
                    st.write(f"**Your answer:** {r['your_answer'] or 'Not answered'}")
                    st.write(f"**Correct answer:** {r['correct_answer']}")
                    st.write(r["explanation"])