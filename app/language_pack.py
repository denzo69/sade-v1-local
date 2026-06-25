from __future__ import annotations

"""Finnish Language Pack v1 for Säde's response prompt."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import re


VERSION = "1.0"
DEFAULT_LANGUAGE = "fi"

TERMINOLOGY: Dict[str, str] = {
    "audit log": "audit-loki",
    "guardrail": "turvaraja",
    "guardrails": "turvarajat",
    "language pack": "kielipaketti",
    "learning feedback": "oppimispalaute",
    "memory cleaner": "muistihuolto (memory_cleaner)",
    "semantic memory": "semanttinen muisti",
    "system prompt": "ydinprompti (system prompt)",
    "tool router": "työkalureititin (tool_router)",
}

PROTECTED_TECHNICAL_FORMS = [
    "API", "FastAPI", "JSON", "JSONL", "RAG", "SHA-256", "UI", "URL",
    "Ollama", "Python", "pytest", "tool_router", "memory_cleaner",
]


def resolve_project_root(project_root: Optional[Path] = None) -> Path:
    if project_root is None:
        return Path(__file__).resolve().parent.parent
    root = Path(project_root).resolve()
    return root.parent if root.name.lower() == "app" else root


def requested_language(message: str) -> str:
    text = " ".join(str(message or "").lower().split())
    english_requests = (
        "answer in english", "reply in english", "respond in english",
        "vastaa englanniksi", "kirjoita englanniksi", "englanniksi kiitos",
    )
    finnish_requests = (
        "answer in finnish", "reply in finnish", "respond in finnish",
        "vastaa suomeksi", "kirjoita suomeksi", "suomeksi kiitos",
    )
    if any(phrase in text for phrase in english_requests):
        return "en"
    if any(phrase in text for phrase in finnish_requests):
        return "fi"
    return DEFAULT_LANGUAGE


def preferred_term(term: str) -> str:
    return TERMINOLOGY.get(str(term or "").strip().lower(), str(term or "").strip())


def build_language_context(message: str, *, concise: bool = False) -> str:
    language = requested_language(message)
    if language == "en":
        return (
            "LANGUAGE: English was explicitly requested. Reply in clear natural English. "
            "Keep code, commands, paths, API names, identifiers and established project names unchanged."
        )

    term_lines = "; ".join(f"{source} → {target}" for source, target in TERMINOLOGY.items())
    length_rule = "Pidä vastaus tiiviinä." if concise else "Sovita vastauksen pituus käyttäjän tarpeeseen."
    return (
        "KIELI: Vastaa oletuksena luontevalla yleiskielisellä suomella. "
        "Älä kirjoita käännöskonemaista tai tarpeettoman muodollista tekstiä. "
        "Säilytä koodi, komennot, tiedostopolut, API-nimet, tunnisteet ja vakiintuneet tuotenimet muuttamattomina. "
        "Kun suomenkielinen termi voisi olla epäselvä, anna ensimmäisellä kerralla myös alkuperäinen tekninen termi sulkeissa. "
        "Älä keksi suomennoksia. Käytä johdonmukaisesti tätä projektisanastoa: "
        f"{term_lines}. {length_rule}"
    )


def inspect_text(text: str) -> Dict[str, Any]:
    value = str(text or "")
    replacement_character_count = value.count("�")
    mojibake_markers = sum(value.count(marker) for marker in ("Ã¤", "Ã¶", "â€”", "â€“"))
    protected_changes = []
    for form in PROTECTED_TECHNICAL_FORMS:
        lowered = form.lower()
        if lowered in value.lower() and form not in value:
            protected_changes.append(form)
    return {
        "ok": replacement_character_count == 0 and mojibake_markers == 0,
        "characters": len(value),
        "replacement_character_count": replacement_character_count,
        "mojibake_marker_count": mojibake_markers,
        "possibly_changed_technical_forms": protected_changes,
    }


def language_status(project_root: Optional[Path] = None) -> Dict[str, Any]:
    root = resolve_project_root(project_root)
    policy_path = root / "docs" / "finnish_language_pack.md"
    return {
        "ok": True,
        "enabled": True,
        "version": VERSION,
        "default_language": DEFAULT_LANGUAGE,
        "explicit_english_supported": True,
        "mode": "prompt_context_and_project_terminology",
        "policy_path": str(policy_path),
        "policy_exists": policy_path.is_file(),
        "terminology_count": len(TERMINOLOGY),
        "protected_technical_forms": PROTECTED_TECHNICAL_FORMS,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "limitations": [
            "Ei ole yleiskäyttöinen konekäännösmoottori.",
            "Ei muuta mallin tuottamaa tekstiä jälkikäteen.",
            "Ohjaa vastausta prompttikontekstilla ja testatulla projektisanastolla.",
        ],
    }

