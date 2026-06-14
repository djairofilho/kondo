import re
import unicodedata
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Attachment, Document
from app.services.content_service import get_document
from app.services.storage_service import storage_service


CHUNK_WORDS = 140
CHUNK_OVERLAP = 35
MAX_CONTEXT_CHARS = 1600

STOPWORDS = {
    "a",
    "as",
    "ao",
    "aos",
    "com",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "ou",
    "para",
    "por",
    "que",
    "se",
    "um",
    "uma",
}


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.lower())
    without_accents = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", without_accents).strip()


def _tokens(value: str) -> list[str]:
    tokens = []
    for token in re.findall(r"[a-z0-9]{3,}", _normalize(value)):
        if token in STOPWORDS:
            continue
        tokens.append(token[:-1] if len(token) > 4 and token.endswith("s") else token)
    return [
        token
        for token in tokens
        if token not in STOPWORDS
    ]


def _clean_text(value: str) -> str:
    cleaned = value.replace("\x00", " ")
    cleaned = re.sub(r"[ \t\r\f\v]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(page for page in pages if page.strip())
        if text.strip():
            return _clean_text(text)
    except Exception:
        pass

    raw = path.read_bytes()
    fallback = raw.decode("utf-8", errors="ignore") or raw.decode("latin-1", errors="ignore")
    visible = re.sub(r"[^A-Za-zÀ-ÿ0-9.,;:!?()/%$@#\-\n ]+", " ", fallback)
    return _clean_text(visible)


def extract_attachment_text(attachment: Attachment) -> str:
    path = storage_service.get_file_path(attachment.storage_key)
    if attachment.content_type == "application/pdf" or path.suffix.lower() == ".pdf":
        return _extract_pdf_text(path)
    return ""


def ingest_document_attachment(db: Session, document_id: int, attachment: Attachment) -> Document:
    document = get_document(db, document_id)
    extracted = extract_attachment_text(attachment)
    if not extracted:
        return document

    prefix = document.content.strip() if document.content else ""
    marker = f"Texto extraido de {attachment.original_file_name}:"
    next_content = f"{prefix}\n\n{marker}\n{extracted}".strip() if prefix else extracted
    document.content = next_content
    if not document.summary:
        document.summary = summarize_document_content(document)
    db.commit()
    db.refresh(document)
    return document


def summarize_document_content(document: Document) -> str:
    content = (document.content or document.summary or "").strip()
    if not content:
        return "Documento cadastrado sem texto pesquisavel."

    sentences = re.split(r"(?<=[.!?])\s+", content)
    summary = " ".join(sentence.strip() for sentence in sentences if sentence.strip())[:700]
    if len(content) > len(summary):
        summary = summary.rstrip(" .,;:") + "..."
    return summary


def retrieve_document_context(document: Document, question: str, limit: int = 3) -> list[str]:
    content = document.content or ""
    words = content.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, CHUNK_WORDS - CHUNK_OVERLAP)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + CHUNK_WORDS]).strip()
        if chunk:
            chunks.append(chunk)

    question_tokens = set(_tokens(question))
    if not question_tokens:
        return chunks[:limit]

    scored: list[tuple[int, int, str]] = []
    for index, chunk in enumerate(chunks):
        chunk_tokens = _tokens(chunk)
        score = sum(1 for token in chunk_tokens if token in question_tokens)
        if score:
            scored.append((score, -index, chunk))

    if not scored:
        return []

    scored.sort(reverse=True)
    selected: list[str] = []
    total = 0
    for _score, _index, chunk in scored[:limit]:
        remaining = MAX_CONTEXT_CHARS - total
        if remaining <= 0:
            break
        selected_chunk = chunk[:remaining].strip()
        selected.append(selected_chunk)
        total += len(selected_chunk)
    return selected


def answer_from_document(document: Document, question: str) -> str:
    contexts = retrieve_document_context(document, question)
    if not contexts:
        return (
            "Nao encontrei um trecho do documento que responda essa pergunta com seguranca. "
            "Tente perguntar com termos mais proximos do texto ou revise se o PDF teve texto extraido."
        )

    context_text = "\n\n".join(f"Trecho {index + 1}: {chunk}" for index, chunk in enumerate(contexts))
    return (
        "Com base no documento, os trechos mais relevantes indicam:\n\n"
        f"{context_text}\n\n"
        "Use essa resposta como apoio e confirme excecoes com a administracao do condominio."
    )
