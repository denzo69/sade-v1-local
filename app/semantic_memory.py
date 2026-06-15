from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib


COLLECTION_NAME = "sade_memory"
DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _import_chromadb():
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        return chromadb, embedding_functions, None
    except Exception as error:
        return None, None, error


def _vector_db_path(project_path: Path) -> Path:
    return project_path / "memory" / "vector_db"


def semantic_memory_status(project_path: Path) -> Dict[str, Any]:
    chromadb, embedding_functions, error = _import_chromadb()
    vector_path = _vector_db_path(project_path)

    if error:
        return {
            "ok": False,
            "enabled": False,
            "message": "ChromaDB ei ole vielä käytettävissä. Asenna riippuvuudet.",
            "error": str(error),
            "vector_path": str(vector_path),
            "collection": COLLECTION_NAME,
            "model": DEFAULT_MODEL_NAME,
        }

    try:
        vector_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(vector_path))
        collection = _get_collection(client, embedding_functions)
        return {
            "ok": True,
            "enabled": True,
            "message": "Semanttinen muisti on käytettävissä.",
            "vector_path": str(vector_path),
            "collection": COLLECTION_NAME,
            "model": DEFAULT_MODEL_NAME,
            "count": collection.count(),
        }
    except Exception as error:
        return {
            "ok": False,
            "enabled": False,
            "message": "Semanttisen muistin tilausta ei voitu lukea.",
            "error": str(error),
            "vector_path": str(vector_path),
            "collection": COLLECTION_NAME,
            "model": DEFAULT_MODEL_NAME,
        }


def _get_collection(client, embedding_functions):
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=DEFAULT_MODEL_NAME
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={
            "description": "Säde v1 semantic memory",
            "model": DEFAULT_MODEL_NAME,
        },
    )


def _stable_id(source: str, text: str, index: int = 0) -> str:
    digest = hashlib.sha256(f"{source}|{index}|{text}".encode("utf-8")).hexdigest()
    return digest[:32]


def split_text_to_chunks(text: str, max_chars: int = 900, overlap_chars: int = 120) -> List[str]:
    cleaned = text.strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = (current + "\n\n" + paragraph).strip() if current else paragraph

        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        start = 0
        while start < len(paragraph):
            end = start + max_chars
            piece = paragraph[start:end].strip()
            if piece:
                chunks.append(piece)
            start = max(0, end - overlap_chars)

        current = ""

    if current:
        chunks.append(current)

    # Lisää pieni päällekkäisyys peräkkäisten chunkkien välille, jotta konteksti ei katkea liian kovaa.
    if overlap_chars > 0 and len(chunks) > 1:
        overlapped: List[str] = []
        previous_tail = ""
        for chunk in chunks:
            combined = (previous_tail + "\n\n" + chunk).strip() if previous_tail else chunk
            overlapped.append(combined)
            previous_tail = chunk[-overlap_chars:].strip()
        chunks = overlapped

    return chunks


def rebuild_semantic_memory_index(project_path: Path, files: Optional[List[Path]] = None) -> Dict[str, Any]:
    chromadb, embedding_functions, error = _import_chromadb()

    if error:
        return {
            "ok": False,
            "message": "ChromaDB ei ole asennettuna tai se ei käynnisty.",
            "error": str(error),
        }

    vector_path = _vector_db_path(project_path)
    vector_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(vector_path))

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = _get_collection(client, embedding_functions)

    if files is None:
        files = [
            project_path / "memory" / "sade_memory.md",
            project_path / "memory" / "chat_log.md",
        ]

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    indexed_files = 0

    for file_path in files:
        if not file_path.exists() or not file_path.is_file():
            continue

        content = file_path.read_text(encoding="utf-8")
        chunks = split_text_to_chunks(content)

        if not chunks:
            continue

        indexed_files += 1

        for index, chunk in enumerate(chunks):
            ids.append(_stable_id(str(file_path), chunk, index))
            documents.append(chunk)
            metadatas.append({
                "source": file_path.name,
                "path": str(file_path),
                "chunk_index": index,
                "indexed_at": datetime.now().isoformat(timespec="seconds"),
            })

    if documents:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    return {
        "ok": True,
        "message": "Semanttinen muisti indeksoitu.",
        "vector_path": str(vector_path),
        "collection": COLLECTION_NAME,
        "model": DEFAULT_MODEL_NAME,
        "indexed_files": indexed_files,
        "chunks": len(documents),
        "count": collection.count(),
    }


def add_text_to_semantic_memory(
    project_path: Path,
    text: str,
    title: Optional[str] = None,
    source: str = "manual",
    tags: Optional[List[str]] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    chromadb, embedding_functions, error = _import_chromadb()

    if error:
        return {
            "ok": False,
            "indexed": False,
            "message": "Muisto tallennettiin tekstitiedostoon, mutta semanttista indeksiä ei päivitetty, koska ChromaDB ei ole käytettävissä.",
            "error": str(error),
        }

    clean_text = text.strip()

    if not clean_text:
        return {
            "ok": False,
            "indexed": False,
            "message": "Tyhjää tekstiä ei indeksoitu.",
        }

    vector_path = _vector_db_path(project_path)
    vector_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(vector_path))
    collection = _get_collection(client, embedding_functions)

    chunks = split_text_to_chunks(clean_text)

    if not chunks:
        return {
            "ok": False,
            "indexed": False,
            "message": "Tekstistä ei syntynyt indeksoitavia paloja.",
        }

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    saved_at = timestamp or datetime.now().isoformat(timespec="seconds")

    for index, chunk in enumerate(chunks):
        ids.append(_stable_id(f"{source}|{title}|{saved_at}", chunk, index))
        documents.append(chunk)
        metadatas.append({
            "source": source,
            "title": title or "",
            "tags": ", ".join(tags or []),
            "chunk_index": index,
            "saved_at": saved_at,
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return {
        "ok": True,
        "indexed": True,
        "message": "Muisto lisätty semanttiseen indeksiin.",
        "chunks": len(documents),
        "count": collection.count(),
        "model": DEFAULT_MODEL_NAME,
    }


def search_semantic_memory(project_path: Path, query: str, n_results: int = 5) -> Dict[str, Any]:
    chromadb, embedding_functions, error = _import_chromadb()

    if error:
        return {
            "ok": False,
            "message": "ChromaDB ei ole asennettuna tai se ei käynnisty.",
            "error": str(error),
            "query": query,
            "results": [],
        }

    clean_query = query.strip()

    if not clean_query:
        return {
            "ok": False,
            "message": "Hakusana ei saa olla tyhjä.",
            "query": query,
            "results": [],
        }

    vector_path = _vector_db_path(project_path)
    vector_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(vector_path))
    collection = _get_collection(client, embedding_functions)

    if collection.count() == 0:
        return {
            "ok": True,
            "message": "Semanttinen muisti on tyhjä. Aja ensin rebuild.",
            "query": query,
            "count": 0,
            "results": [],
        }

    raw = collection.query(
        query_texts=[clean_query],
        n_results=max(1, min(int(n_results), 20)),
        include=["documents", "metadatas", "distances"],
    )

    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    results = []

    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = distances[index] if index < len(distances) else None

        results.append({
            "rank": index + 1,
            "distance": distance,
            "metadata": metadata,
            "text": document,
        })

    return {
        "ok": True,
        "message": "Semanttinen haku valmis.",
        "query": query,
        "count": len(results),
        "results": results,
    }


def format_semantic_context(search_result: Dict[str, Any], max_chars: int = 3500) -> str:
    if not search_result.get("ok"):
        return ""

    results = search_result.get("results") or []

    if not results:
        return ""

    parts: List[str] = []

    for item in results:
        metadata = item.get("metadata") or {}
        source = metadata.get("source", "tuntematon")
        title = metadata.get("title", "")
        distance = item.get("distance")
        distance_text = f"{distance:.4f}" if isinstance(distance, (int, float)) else "?"

        header = f"[{item.get('rank', '?')}] Lähde: {source}"
        if title:
            header += f" | Otsikko: {title}"
        header += f" | distance: {distance_text}"

        parts.append(header + "\n" + str(item.get("text", "")).strip())

    context = "\n\n---\n\n".join(parts).strip()

    if len(context) <= max_chars:
        return context

    return context[:max_chars].rstrip() + "\n\n[Semanttinen muistihaku katkaistu pituuden vuoksi.]"
