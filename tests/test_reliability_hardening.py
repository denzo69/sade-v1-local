from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest

from app import rag_engine, tool_router, web_search
from app.model_provider import ModelProviderError, OllamaProvider, provider_from_config


def test_model_provider_rejects_unknown_provider() -> None:
    with pytest.raises(ModelProviderError) as error:
        provider_from_config({"model_provider": "openai"})

    assert "Tuntematon model_provider" in str(error.value)


def test_ollama_provider_wraps_connection_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(*_args, **_kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = OllamaProvider(url="http://127.0.0.1:11434/api/generate", model="test-model")

    with pytest.raises(ModelProviderError) as error:
        provider.generate("hello", timeout=1)

    assert "Ollamaan" in str(error.value)
    assert "offline" in str(error.value)


def test_ollama_provider_strips_response_text(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return json.dumps({"response": "  visible reply  "}).encode("utf-8")

    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: FakeResponse())
    provider = OllamaProvider(url="http://127.0.0.1:11434/api/generate", model="test-model")

    result = provider.generate("hello", timeout=1)

    assert result.text == "visible reply"
    assert result.provider == "ollama"
    assert result.model == "test-model"


def test_web_search_unknown_provider_is_cached_as_failure(tmp_path: Path) -> None:
    result = web_search.web_search(tmp_path, "ai ethics", provider="unknown-provider")

    assert result["ok"] is False
    assert result["provider"] == "unknown-provider"
    assert result["results"] == []
    assert "Tuntematon provider" in result["error"]
    assert Path(result["cache_path"]).exists()


def test_web_search_empty_query_does_not_create_cache(tmp_path: Path) -> None:
    result = web_search.web_search(tmp_path, "   ", provider="duckduckgo_lite")

    assert result["ok"] is False
    assert result["message"] == "Hakukysely puuttuu."
    assert not (tmp_path / "memory" / "web_search_cache").exists()


def test_brave_search_parses_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-key")

    def fake_get(url: str, *, headers=None, **_kwargs):
        assert "api.search.brave.com" in url
        assert headers["X-Subscription-Token"] == "test-key"
        return json.dumps(
            {
                "web": {
                    "results": [
                        {
                            "title": "Brave result",
                            "url": "https://example.org/article",
                            "description": "A useful snippet.",
                        }
                    ]
                }
            }
        )

    monkeypatch.setattr("app.web_search._http_get", fake_get)

    results = web_search.brave_search("ai safety")

    assert len(results) == 1
    assert results[0].title == "Brave result"
    assert results[0].source == "example.org"


def test_google_search_requires_api_key_and_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_SEARCH_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_SEARCH_ENGINE_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CSE_ID", raising=False)

    with pytest.raises(RuntimeError, match="GOOGLE_SEARCH_API_KEY"):
        web_search.google_search("ai safety")

    monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "test-key")

    with pytest.raises(RuntimeError, match="GOOGLE_SEARCH_ENGINE_ID"):
        web_search.google_search("ai safety")


def test_inspect_source_rejects_private_or_non_http_urls() -> None:
    assert web_search.inspect_source("file:///C:/secret.txt")["ok"] is False
    assert web_search.inspect_source("http://localhost:8080/admin")["ok"] is False


def test_source_review_without_successful_search_is_truthful(tmp_path: Path) -> None:
    result = web_search.review_latest_search_sources(tmp_path)
    reply = web_search.format_source_review_reply(result)

    assert result["ok"] is False
    assert result["sources"] == []
    assert "ei onnistunut" in reply


def test_duckduckgo_parser_deduplicates_and_ignores_noise() -> None:
    parser = web_search.DuckDuckGoLiteParser()
    parser.feed(
        """
        <a href="/lite/">noise</a>
        <a href="/l/?kh=-1&uddg=https%3A%2F%2Fexample.com%2Fa">Example A</a>
        <a href="/l/?kh=-1&uddg=https%3A%2F%2Fexample.com%2Fa">Duplicate A</a>
        <a href="https://www.duckduckgo.com/about">DuckDuckGo</a>
        <a href="https://example.com/b">Example B</a>
        """
    )

    assert [item.url for item in parser.results] == ["https://example.com/a", "https://example.com/b"]
    assert parser.results[0].source == "example.com"


def test_source_page_parser_collects_title_description_and_visible_text() -> None:
    parser = web_search.SourcePageParser()
    parser.feed(
        """
        <html>
          <head>
            <title>Weather Page</title>
            <meta name="description" content="Lieksa weather summary">
            <style>.hidden { display:none }</style>
            <script>secret()</script>
          </head>
          <body><h1>Forecast</h1><p>Temperature +12 °C and light wind.</p></body>
        </html>
        """
    )

    assert "Weather Page" in " ".join(parser.title_parts)
    assert parser.description == "Lieksa weather summary"
    assert "Forecast" in " ".join(parser.text_parts)
    assert "secret" not in " ".join(parser.text_parts)


def test_web_search_success_writes_cache_and_serializes_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.web_search.duckduckgo_lite_search",
        lambda query, max_results=6: [
            web_search.WebSearchResult(
                title="Cached result",
                url="https://example.com/cached",
                source="example.com",
                snippet="Snippet",
                rank=1,
            )
        ],
    )

    result = web_search.web_search(tmp_path, "cached query", provider="duckduckgo_lite")

    assert result["ok"] is True
    assert result["results"][0]["title"] == "Cached result"
    cached = json.loads(Path(result["cache_path"]).read_text(encoding="utf-8"))
    assert cached["query"] == "cached query"
    assert cached["results"][0]["url"] == "https://example.com/cached"


def test_build_source_based_answer_handles_weather_without_numeric_observation() -> None:
    answer = web_search.build_source_based_answer(
        "sää Lieksa",
        [
            {
                "ok": True,
                "source": "foreca.fi",
                "title": "Foreca",
                "description": "Forecast page opened, but no compact value was extracted.",
            }
        ],
    )

    assert "en saanut sivuilta varmasti poimittua" in answer
    assert "foreca.fi" in answer


def test_build_source_based_answer_summarizes_general_excerpts() -> None:
    answer = web_search.build_source_based_answer(
        "AI governance",
        [
            {"ok": True, "title": "Report A", "description": "AI governance requires transparency and oversight."},
            {"ok": True, "title": "Report B", "preview": "Risk management should be documented."},
        ],
    )

    assert "Tarkistettujen lähteiden perusteella" in answer
    assert "Report A" in answer
    assert "Risk management" in answer


def test_rag_chat_log_is_excluded_unless_requested(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = rag_engine.RagCandidate(
        source_type="chat_log",
        source="chat_log.md",
        path="memory/chat_log.md",
        title="Chat log",
        text="important deployment rollback policy",
        origin="chat_log",
    )

    monkeypatch.setattr("app.rag_engine._learning_review_candidates", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("app.rag_engine._sade_memory_candidates", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("app.rag_engine._important_upload_candidates", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("app.rag_engine._semantic_candidates", lambda *_args, **_kwargs: [candidate])

    excluded = rag_engine.rag_search(tmp_path, "deployment rollback policy", min_score=0)
    included = rag_engine.rag_search(tmp_path, "deployment rollback policy", include_chat_log=True, min_score=0)

    assert excluded["count"] == 0
    assert included["count"] == 1
    assert included["results"][0]["source_type"] == "chat_log"


def test_rag_source_classification_and_similarity_edges() -> None:
    assert rag_engine._classify_source("learning_reviews.jsonl", "memory/learning_reviews.jsonl", "") == "learning_review"
    assert rag_engine._classify_source("Sade_Operating_Manual.md", "docs/Sade_Operating_Manual.md", "") == "operating_manual"
    assert rag_engine._classify_source("memory_policy.md", "docs/memory_policy.md", "") == "atlas"
    assert rag_engine._classify_source("sade_memory.md", "memory/sade_memory.md", "") == "sade_memory"
    assert rag_engine._classify_source("chat_log.md", "memory/chat_log.md", "") == "chat_log"
    assert rag_engine._classify_source("notes.md", "uploads/notes.md", "") == "uploaded_file"
    assert rag_engine._classify_source("README.md", "README.md", "") == "project_doc"
    assert rag_engine._classify_source("unknown.bin", "misc/unknown.bin", "") == "unknown"

    assert rag_engine._semantic_similarity_from_distance(None) == 0.0
    assert rag_engine._semantic_similarity_from_distance("not-a-number") == 0.0
    assert rag_engine._semantic_similarity_from_distance(float("nan")) == 0.0
    assert rag_engine._semantic_similarity_from_distance(0) == 35.0


def test_rag_candidate_scoring_penalizes_partial_or_unrelated_matches() -> None:
    unrelated = rag_engine.RagCandidate(
        source_type="project_doc",
        source="doc.md",
        path="docs/doc.md",
        title="Doc",
        text="nothing relevant here",
    )
    partial = rag_engine.RagCandidate(
        source_type="project_doc",
        source="security.md",
        path="docs/security.md",
        title="Security",
        text="security only",
    )
    exact = rag_engine.RagCandidate(
        source_type="project_doc",
        source="security-policy.md",
        path="docs/security-policy.md",
        title="Security Policy",
        text="security policy",
    )

    unrelated = rag_engine._score_candidate(unrelated, "security policy rollback")
    partial = rag_engine._score_candidate(partial, "security policy rollback")
    exact = rag_engine._score_candidate(exact, "security policy")

    assert any("coverage_penalty" in reason for reason in partial.reasons or [])
    assert exact.score > partial.score > unrelated.score
    assert exact.exact_phrase is True


def test_rag_chunking_trims_and_limits_per_path() -> None:
    text = "# One\n\nA" * 800 + "\n# Two\n\nB" * 800
    chunks = rag_engine._chunk_markdownish(text, max_chars=200)
    trimmed = rag_engine._trim_text("x" * 300, max_chars=50)

    candidates = [
        rag_engine.RagCandidate("project_doc", "same.md", "docs/same.md", "A", "alpha", score=10),
        rag_engine.RagCandidate("project_doc", "same.md", "docs/same.md", "B", "beta", score=9),
        rag_engine.RagCandidate("project_doc", "same.md", "docs/same.md", "C", "gamma", score=8),
    ]

    assert len(chunks) >= 2
    assert trimmed.endswith("...[katkaistu]")
    assert len(rag_engine._limit_per_path(candidates, max_per_path=2)) == 2


def test_rag_learning_review_candidates_from_jsonl_and_markdown(tmp_path: Path) -> None:
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "learning_reviews.jsonl").write_text(
        json.dumps(
            {
                "title": "RAG Reliability",
                "relative_path": "uploads/rag_notes.md",
                "terms": ["rag", "retrieval"],
                "learning_points": ["RAG retrieval needs source-aware tests."],
                "project_relevance": ["Improves reliability."],
                "remember_later": ["Check source quality."],
                "future_tasks": ["Add regression tests."],
                "markdown": "# RAG Reliability\n\nretrieval source quality",
                "review_id": "lr-1",
            }
        )
        + "\nnot-json\n",
        encoding="utf-8",
    )
    (memory / "learning_reviews.md").write_text("# Extra RAG note\n\nretrieval quality policy", encoding="utf-8")

    results = rag_engine._learning_review_candidates(tmp_path, "rag retrieval quality")

    assert results
    assert all(item.source_type == "learning_review" for item in results)
    assert any(item.origin == "learning_review_log" for item in results)


def test_rag_important_upload_candidates_only_include_curated_files(tmp_path: Path) -> None:
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    (uploads / "random.txt").write_text("rag retrieval quality", encoding="utf-8")
    (uploads / "rag_policy_notes.md").write_text("rag retrieval quality", encoding="utf-8")

    results = rag_engine._important_upload_candidates(tmp_path, "rag retrieval quality")

    assert len(results) == 1
    assert results[0].path == "uploads/rag_policy_notes.md"


def test_rag_strict_document_query_filters_unrelated_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wrong = rag_engine.RagCandidate(
        source_type="project_doc",
        source="random.md",
        path="docs/random.md",
        title="Random note",
        text="operating manual",  # content hit, but metadata does not identify the requested document
        origin="lexical",
    )
    right = rag_engine.RagCandidate(
        source_type="operating_manual",
        source="Sade_Operating_Manual.md",
        path="docs/Sade_Operating_Manual.md",
        title="Operating Manual",
        text="operating manual",
        origin="lexical",
    )

    monkeypatch.setattr("app.rag_engine._learning_review_candidates", lambda *_args, **_kwargs: [wrong, right])
    monkeypatch.setattr("app.rag_engine._sade_memory_candidates", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("app.rag_engine._important_upload_candidates", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("app.rag_engine._semantic_candidates", lambda *_args, **_kwargs: [])

    result = rag_engine.rag_search(tmp_path, "operating manual", min_score=0)

    assert result["count"] == 1
    assert result["results"][0]["source_type"] == "operating_manual"


def test_rag_lexical_candidates_skip_blocked_and_binary_paths(tmp_path: Path) -> None:
    blocked_dir = tmp_path / ".git"
    blocked_dir.mkdir()
    blocked_file = blocked_dir / "config.md"
    blocked_file.write_text("deployment rollback policy", encoding="utf-8")

    binary_file = tmp_path / "docs" / "manual.exe"
    binary_file.parent.mkdir()
    binary_file.write_text("deployment rollback policy", encoding="utf-8")

    assert rag_engine._lexical_candidates_from_file(tmp_path, blocked_file, "deployment rollback policy", "project_doc", "test") == []
    assert rag_engine._lexical_candidates_from_file(tmp_path, binary_file, "deployment rollback policy", "project_doc", "test") == []


def test_tool_router_failed_web_search_returns_no_actions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_failed_search(_root: Path, query: str, max_results: int = 6):
        return {"ok": False, "query": query, "provider": "test", "error": "offline", "results": []}

    monkeypatch.setattr("app.web_search.web_search", fake_failed_search)

    result = tool_router.route_tool_request(tmp_path, "hae verkosta ai ethics")

    assert result["handled"] is True
    assert result["tool"] == "web_search"
    assert result["actions"] == []
    assert "Verkkohaku ei onnistunut" in result["reply"]


def test_tool_router_pending_search_can_be_cancelled(tmp_path: Path) -> None:
    start = tool_router.route_tool_request(tmp_path, "kokeillaan verkkohakua")
    cancel = tool_router.route_tool_request(tmp_path, "peru")

    assert start["tool"] == "web_search_pending"
    assert cancel["handled"] is False


def test_tool_router_common_file_tools_route_through_guarded_layer(tmp_path: Path) -> None:
    write = tool_router.route_tool_request(tmp_path, "luo tiedosto docs/router.md: Hello router")
    append = tool_router.route_tool_request(tmp_path, "appendaa tiedostoon docs/router.md: toinen rivi")
    read = tool_router.route_tool_request(tmp_path, "lue tiedosto docs/router.md")
    listed = tool_router.route_tool_request(tmp_path, "listaa kansio docs")

    assert write["tool"] == "write_file"
    assert append["tool"] == "append_file"
    assert read["tool"] == "read_file"
    assert listed["tool"] == "list_files"
    assert "Hello router" in read["reply"]
    assert "docs" in listed["reply"]


def test_tool_router_missing_paths_return_helpful_tool_responses(tmp_path: Path) -> None:
    read = tool_router.route_tool_request(tmp_path, "lue tiedosto")
    write = tool_router.route_tool_request(tmp_path, "luo tiedosto")
    summarize = tool_router.route_tool_request(tmp_path, "summarize file")
    ingest = tool_router.route_tool_request(tmp_path, "ingest file")

    assert read["tool"] == "read_file"
    assert "Anna luettava tiedosto" in read["reply"]
    assert write["tool"] == "write_or_append_file"
    assert "Käytä muotoa" in write["reply"]
    assert summarize["tool"] == "summarize_file"
    assert "Anna tiivistettävä tiedosto" in summarize["reply"]
    assert ingest["tool"] == "ingest_file"
    assert "Anna käsiteltävä tiedosto" in ingest["reply"]


def test_tool_router_semantic_search_routes_and_handles_missing_query(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.tool_router.search_semantic_memory",
        lambda root, query, n_results=5: {
            "ok": True,
            "query": query,
            "count": 1,
            "results": [{"text": "memory hit", "metadata": {"source": "unit-test"}}],
        },
    )

    missing = tool_router.route_tool_request(tmp_path, "semantic search")
    found = tool_router.route_tool_request(tmp_path, "semantic search portfolio")

    assert missing["tool"] == "semantic_search"
    assert "Anna vielä hakusana" in missing["reply"]
    assert found["tool"] == "semantic_search"
    assert "memory hit" in found["reply"]


def test_tool_router_logs_and_status_routes(tmp_path: Path) -> None:
    tools_status = tool_router.route_tool_request(tmp_path, "tools status")
    tools_list = tool_router.route_tool_request(tmp_path, "list tools")
    project_status = tool_router.route_tool_request(tmp_path, "project status")
    tool_log = tool_router.route_tool_request(tmp_path, "tool log")
    ingestion_log = tool_router.route_tool_request(tmp_path, "ingestion log")

    assert tools_status["tool"] == "tools_status"
    assert tools_list["tool"] == "list_tools"
    assert project_status["tool"] == "project_status"
    assert tool_log["tool"] == "read_tool_log"
    assert ingestion_log["tool"] == "read_ingestion_log"
    assert "tyhjä" in tool_log["reply"].lower()
    assert "tyhjä" in ingestion_log["reply"].lower()


def test_tool_router_catches_tool_errors_for_unsafe_paths(tmp_path: Path) -> None:
    result = tool_router.route_tool_request(tmp_path, "lue tiedosto ../secret.txt")

    assert result["tool"] == "tool_error"
    assert result["result"]["ok"] is False
    assert "Työkalu ei voinut" in result["reply"]
