# 📚 Lecture Notes Summarizer + Quiz Generator

An AI web app that turns a lecture PDF or YouTube video into study notes and a practice MCQ quiz.

## Features
- Input: PDF upload or YouTube link (uses the video transcript)
- Handles long material: cleaning, chunking (LangChain) and map-reduce summarization
- Quiz: 3-10 MCQs, validated with Pydantic, options shuffled, auto-scored with answer review
- Output language: English / Hindi / Hinglish
- Streamlit interface

## Tech stack
Python, LangChain, Gemini API, PyMuPDF, youtube-transcript-api, Pydantic, Streamlit

## Setup
```
git clone https://github.com/Shivam-jain-create/lecture-notes-quiz-ai.git
cd lecture-notes-quiz-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```
Open `.env` and add your own Google AI Studio API key.

## Project structure
- `app.py` - Streamlit interface
- `extractor.py` - PDF text and YouTube transcript extraction
- `chunker.py` - text cleaning and chunking
- `llm_chain.py` - prompts, summarization and quiz generation
- `validator.py` - quiz schema and validation
- `quiz.py` - option shuffling and scoring

## Limitations
- Only the first N chunks are processed (free API rate limits)
- The quiz is generated from the summary, so summary errors can carry over
- Auto-generated YouTube captions can be inaccurate
- Scanned (image-only) PDFs are not supported