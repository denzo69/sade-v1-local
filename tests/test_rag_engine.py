from pathlib import Path
from app.rag_engine import RagCandidate, rag_search


def test_rag_search_uses_semantic_candidates_without_writing_memory(tmp_path: Path, monkeypatch) -> None:
    candidate = RagCandidate(source_type="project_doc", source="policy.md", path="docs/policy.md", title="Etiikka", text="tekoälyn etiikka ja läpinäkyvyys", origin="semantic_memory")
    monkeypatch.setattr("app.rag_engine._learning_review_candidates", lambda root, query: [])
    monkeypatch.setattr("app.rag_engine._sade_memory_candidates", lambda root, query: [])
    monkeypatch.setattr("app.rag_engine._important_upload_candidates", lambda root, query: [])
    monkeypatch.setattr("app.rag_engine._semantic_candidates", lambda root, query, n_results=12: [candidate])
    result = rag_search(tmp_path, "tekoälyn etiikka", min_score=0)
    assert result["ok"] is True
    assert result["count"] == 1
    assert result["results"][0]["origin"] == "semantic_memory"
    assert not (tmp_path / "memory").exists()


def test_rag_search_rejects_empty_query(tmp_path: Path) -> None:
    result = rag_search(tmp_path, "   ")
    assert result["ok"] is False
    assert result["results"] == []

