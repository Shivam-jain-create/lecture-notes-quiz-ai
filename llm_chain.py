import os
import time

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from validator import Quiz

load_dotenv()

SYSTEM_MSG = (
    "You are a study assistant for university students. "
    "Use ONLY the text provided. Do not add facts that are not in the text. "
    "Write your answer in {language}."
)

CHUNK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MSG),
    ("human",
     "Summarize this part of a lecture in 4-6 concise bullet points. "
     "Keep important definitions, formulas and examples.\n\n{text}"),
])

FINAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MSG),
    ("human",
     "Below are summaries of consecutive parts of one lecture. "
     "Combine them into one well-organized set of study notes: "
     "a 2-line overview, then the main topics as headings with bullet points. "
     "Remove repetition.\n\n{text}"),
])


def get_llm(temperature: float = 0.3):
    return ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=temperature,
    )


def _call_with_retry(chain, inputs: dict, retries: int = 3):
    """Free-tier APIs fail sometimes (rate limits). Wait and try again."""
    for attempt in range(retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 10 * (attempt + 1)
            print(f"  API error ({type(e).__name__}), retrying in {wait}s...")
            time.sleep(wait)


def summarize_chunks(chunks: list[str], language: str = "English",
                     delay: float = 4.0, progress=None) -> list[str]:
    """MAP step: summarize every chunk separately."""
    chain = CHUNK_PROMPT | get_llm() | StrOutputParser()
    summaries = []
    for i, chunk in enumerate(chunks, start=1):
        summaries.append(_call_with_retry(chain, {"text": chunk, "language": language}))
        if progress:
            progress(i, len(chunks))
        if i < len(chunks):
            time.sleep(delay)  # stay under the free-tier requests-per-minute limit
    return summaries


def combine_summaries(summaries: list[str], language: str = "English") -> str:
    """REDUCE step: merge all chunk summaries into final notes."""
    chain = FINAL_PROMPT | get_llm() | StrOutputParser()
    joined = "\n\n".join(f"Part {i}:\n{s}" for i, s in enumerate(summaries, start=1))
    return _call_with_retry(chain, {"text": joined, "language": language})


def summarize_text(chunks: list[str], language: str = "English",
                   delay: float = 4.0, progress=None) -> str:
    parts = summarize_chunks(chunks, language, delay, progress)
    return combine_summaries(parts, language)

QUIZ_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MSG),
    ("human",
     "Create {num_questions} multiple-choice questions from these study notes. "
     "Each question must have exactly 4 options and exactly one correct answer. "
     "Make the wrong options plausible, not silly. "
     "Only ask about facts that appear in the notes.\n\n{text}"),
])


def generate_quiz(notes: str, num_questions: int = 5, language: str = "English") -> Quiz:
    """Turn study notes into a validated Quiz object."""
    structured_llm = get_llm(temperature=0.4).with_structured_output(Quiz)
    chain = QUIZ_PROMPT | structured_llm
    quiz = _call_with_retry(chain, {"text": notes, "num_questions": num_questions, "language": language})
    quiz.questions = quiz.questions[:num_questions]
    return quiz


if __name__ == "__main__":
    from extractor import extract_text_from_pdf
    from chunker import clean_text, chunk_text

    text = clean_text(extract_text_from_pdf("samples/sample.pdf"))
    chunks = chunk_text(text)[:5]  # only 5 chunks while testing
    print(f"Testing with {len(chunks)} chunks...")

    final = summarize_text(chunks, progress=lambda i, n: print(f"  chunk {i}/{n} done"))
    print("\n=== FINAL NOTES ===\n")
    print(final)