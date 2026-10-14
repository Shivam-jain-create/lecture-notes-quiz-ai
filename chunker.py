import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


def clean_text(text: str) -> str:
    """Remove extra spaces and blank lines left over from PDF/transcript extraction."""
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)        # many spaces -> one
    text = re.sub(r"\n\s*\n+", "\n\n", text)   # many blank lines -> one
    return text.strip()


def chunk_text(text: str, chunk_size: int = 4000, chunk_overlap: int = 300) -> list[str]:
    """Split long text into overlapping chunks that fit in one LLM request."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)


if __name__ == "__main__":
    from extractor import extract_text_from_pdf

    raw = extract_text_from_pdf("samples/sample.pdf")
    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned)

    print("Raw chars:", len(raw))
    print("Cleaned chars:", len(cleaned))
    print("Chunks:", len(chunks))
    print("First 5 chunk sizes:", [len(c) for c in chunks[:5]])
    print("\n--- END of chunk 0 ---")
    print(chunks[0][-300:])
    print("\n--- START of chunk 1 ---")
    print(chunks[1][:300])