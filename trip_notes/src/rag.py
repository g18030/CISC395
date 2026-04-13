import os
from pathlib import Path

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

GUIDES_DIR = "guides"
DB_PATH = "chroma_db"
COLLECTION = "trip_guides"
CHUNK_SIZE = 200  # words
CHUNK_OVERLAP = 30  # words


def read_file(path: str) -> str:
    file_path = Path(path)

    try:
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md"}:
            text = file_path.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            reader = PdfReader(str(file_path))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            return ""
    except Exception as err:
        print(f"Warning: could not read {file_path.name}: {err}")
        return ""

    if not text.strip():
        print(
            f"Warning: {file_path.name} has no extractable text (scanned PDF?), skipping."
        )
        return ""

    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if not words:
        return []

    step = max(1, chunk_size - overlap)
    chunks: list[str] = []

    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            continue
        chunks.append(" ".join(chunk_words))

    return chunks


def build_index(force: bool = False):
    if not os.path.isdir(GUIDES_DIR):
        print("Error: guides/ folder not found.")
        return

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION)

    existing_ids: set[str] = set()
    if force:
        existing = collection.get()
        ids_to_delete = existing.get("ids", []) if isinstance(existing, dict) else []
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
    else:
        existing = collection.get()
        existing_ids = set(existing.get("ids", [])) if isinstance(existing, dict) else set()

    guides_path = Path(GUIDES_DIR)
    files = [
        p
        for p in guides_path.iterdir()
        if p.is_file() and p.suffix.lower() in {".txt", ".md", ".pdf"}
    ]

    if not files:
        print("Warning: no supported files found in guides/.")
        return

    model = SentenceTransformer("all-MiniLM-L6-v2")
    total_chunks_added = 0
    files_indexed = 0

    for file_path in files:
        text = read_file(str(file_path))
        if text == "":
            continue

        chunks = chunk_text(text)
        if not chunks:
            continue

        ids_to_add: list[str] = []
        docs_to_add: list[str] = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_path.stem}_chunk_{i}"
            if not force and chunk_id in existing_ids:
                continue
            ids_to_add.append(chunk_id)
            docs_to_add.append(chunk)
            existing_ids.add(chunk_id)

        if not docs_to_add:
            continue

        embeddings = model.encode(docs_to_add).tolist()
        collection.add(ids=ids_to_add, documents=docs_to_add, embeddings=embeddings)

        total_chunks_added += len(docs_to_add)
        files_indexed += 1

    print(f"Indexed {total_chunks_added} chunks from {files_indexed} files.")


def ensure_index() -> object:
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION)

    if collection.count() == 0:
        print("No index found. Building from guides/...")
        build_index()

    return collection


def search_guides(query: str, n_results: int = 3) -> list[str]:
    collection = ensure_index()

    if collection.count() == 0:
        return []

    model = SentenceTransformer("all-MiniLM-L6-v2")
    vector = model.encode(query).tolist()

    n_results = min(n_results, collection.count())
    results = collection.query(query_embeddings=[vector], n_results=n_results)
    return results["documents"][0]


if __name__ == "__main__":
    build_index()
