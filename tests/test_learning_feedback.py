from pathlib import Path

from app.learning_feedback import build_feedback_context, parse_feedback_message, read_feedback, record_feedback
from app.tool_router import route_tool_request


def test_feedback_is_structured_redacted_and_not_written_to_semantic_memory(tmp_path: Path) -> None:
    result = record_feedback(tmp_path, original="Vastaus oli X", correction="Oikea arvo on Y token=secret-value", tags=["test"])
    assert result["ok"] is True
    assert result["entry"]["semantic_memory_written"] is False
    assert "secret-value" not in result["entry"]["correction"]
    assert read_feedback(tmp_path)["count"] == 1
    assert "Oikea arvo" in build_feedback_context(tmp_path)


def test_feedback_chat_route_records_explicit_correction(tmp_path: Path) -> None:
    parsed = parse_feedback_message("korjaus: hauki on nisäkäs -> hauki on kala")
    result = route_tool_request(tmp_path, "korjaus: hauki on nisäkäs -> hauki on kala")
    assert parsed == {"original": "hauki on nisäkäs", "correction": "hauki on kala"}
    assert result["tool"] == "learning_feedback"
    assert read_feedback(tmp_path)["count"] == 1

