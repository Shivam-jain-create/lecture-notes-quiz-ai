from urllib.parse import urlparse, parse_qs

import pymupdf
from youtube_transcript_api import YouTubeTranscriptApi


def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF. `file` can be a file path or raw bytes."""
    if isinstance(file, (bytes, bytearray)):
        doc = pymupdf.open(stream=file, filetype="pdf")
    else:
        doc = pymupdf.open(file)

    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    doc.close()

    full_text = "\n".join(pages).strip()
    if not full_text:
        raise ValueError("No text found. This PDF may be scanned (image-only).")
    return full_text


def get_video_id(url: str) -> str:
    """Pull the video ID out of the common YouTube link formats."""
    parsed = urlparse(url.strip())
    host = parsed.netloc.replace("www.", "")

    video_id = ""
    if host == "youtu.be":
        video_id = parsed.path.lstrip("/")
    elif host in ("youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/")):
            video_id = parsed.path.split("/")[2]

    if not video_id:
        raise ValueError("Invalid YouTube link.")
    return video_id


def extract_text_from_youtube(url: str) -> str:
    """Fetch the transcript of a YouTube video as one string."""
    video_id = get_video_id(url)
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=["en", "hi"])
    except Exception as e:
        raise ValueError(f"Could not get transcript (captions may be disabled): {e}")

    text = " ".join(snippet.text for snippet in fetched).strip()
    if not text:
        raise ValueError("Transcript is empty.")
    return text


if __name__ == "__main__":
    url = input("YouTube link: ")
    text = extract_text_from_youtube(url)
    print("Characters:", len(text))
    print(text[:500])