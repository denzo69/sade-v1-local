from pathlib import Path
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

