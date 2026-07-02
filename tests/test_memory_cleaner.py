from pathlib import Path
from datetime import datetime, timedelta, timezone
from app.memory_cleaner import CONFIRMATION_PHRASE, apply_memory_cleanup, plan_memory_cleanup


class FakeCollection:
    def __init__(self):
        self.ids = ["a", "b", "protected"]
        self.documents = ["sama teksti", "sama teksti", "pysyvä tieto"]
        self.metadatas = [{"source": "chat_log.md"}, {"source": "chat_log.md"}, {"source": "sade_memory.md"}]
    def get(self, include):
        return {"ids": list(self.ids), "documents": list(self.documents), "metadatas": list(self.metadatas)}
    def count(self):
        return len(self.ids)
    def delete(self, ids):
        self.ids = [item for item in self.ids if item not in ids]


def test_memory_cleaner_preview_protects_long_term_memory(tmp_path: Path, monkeypatch) -> None:
    collection = FakeCollection()
    monkeypatch.setattr("app.memory_cleaner._open_collection", lambda root: collection)
    plan = plan_memory_cleanup(tmp_path)
    assert plan["dry_run"] is True
    assert [item["id"] for item in plan["candidates"]] == ["b"]
    assert "protected" not in [item["id"] for item in plan["candidates"]]


def test_memory_cleaner_requires_confirmation_and_only_deletes_candidates(tmp_path: Path, monkeypatch) -> None:
    collection = FakeCollection()
    monkeypatch.setattr("app.memory_cleaner._open_collection", lambda root: collection)
    denied = apply_memory_cleanup(tmp_path, ["b"], confirmation="kyllä")
    approved = apply_memory_cleanup(tmp_path, ["b", "protected"], confirmation=CONFIRMATION_PHRASE)
    assert denied["deleted"] == 0
    assert approved["deleted"] == 1
    assert "protected" in collection.ids


def test_memory_cleaner_handles_collection_errors(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("app.memory_cleaner._open_collection", lambda root: (_ for _ in ()).throw(RuntimeError("no chroma")))

    plan = plan_memory_cleanup(tmp_path)

    assert plan["ok"] is False
    assert plan["dry_run"] is True
    assert plan["candidates"] == []
    assert "no chroma" in plan["error"]


def test_memory_cleaner_marks_old_chat_log_and_ignores_bad_dates(tmp_path: Path, monkeypatch) -> None:
    old_date = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()

    class OldCollection:
        ids = ["old", "bad-date", "manual"]
        documents = ["old chat", "bad date chat", "manual memory"]
        metadatas = [
            {"source": "chat_log.md", "saved_at": old_date},
            {"source": "chat_log.md", "saved_at": "not-a-date"},
            {"source": "manual", "saved_at": old_date},
        ]
        def get(self, include):
            return {"ids": self.ids, "documents": self.documents, "metadatas": self.metadatas}
        def count(self):
            return len(self.ids)

    monkeypatch.setattr("app.memory_cleaner._open_collection", lambda root: OldCollection())

    plan = plan_memory_cleanup(tmp_path, older_than_days=180)

    assert [item["id"] for item in plan["candidates"]] == ["old"]
    assert plan["candidates"][0]["reason"] == "old_chat_log"


def test_memory_cleaner_rejects_non_candidate_ids_after_confirmation(tmp_path: Path, monkeypatch) -> None:
    collection = FakeCollection()
    monkeypatch.setattr("app.memory_cleaner._open_collection", lambda root: collection)

    result = apply_memory_cleanup(tmp_path, ["not-a-candidate"], confirmation=CONFIRMATION_PHRASE)

    assert result["ok"] is False
    assert result["deleted"] == 0
