from __future__ import annotations

"""
Säde v1 - Persona Layer v1

Tarkoitus:
- Ei päättele "totuutta" itse.
- Ei muuta tiedostoja.
- Ei aja komentoja.
- Muotoilee introspection.py:n tai muun statusraportin Säteen dokumentoidulla äänellä.
- Lukee kevyesti persona_state.json-, sade_identity_core.md-, self_model_policy.md- ja
  autobiographical_memory.md-tiedostoja, jos ne löytyvät.

Suositeltu sijainti:
    C:\\Sade\\Sade-v1\\app\\persona_layer.py

Testaus:
    cd C:\\Sade\\Sade-v1
    python app\\persona_layer.py --status
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def resolve_project_root(project_root: Optional[Path] = None) -> Path:
    """
    Palauttaa projektijuuren.

    Jos tiedosto sijaitsee app/persona_layer.py:
        Path(__file__).resolve().parent.parent -> C:\\Sade\\Sade-v1

    Jos funktiolle annetaan app-kansio, palautetaan sen parent.
    """
    if project_root is None:
        return Path(__file__).resolve().parent.parent

    root = Path(project_root).resolve()
    if root.name.lower() == "app":
        return root.parent
    return root


def _read_text(path: Path, max_chars: Optional[int] = None) -> str:
    try:
        if not path.is_file():
            return ""
        text = path.read_text(encoding="utf-8")
        if max_chars is not None and len(text) > max_chars:
            return text[:max_chars] + "\n\n...[katkaistu]..."
        return text
    except Exception:
        return ""


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.is_file():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _first_existing(root: Path, candidates: Iterable[str]) -> Optional[Path]:
    for relative in candidates:
        path = root / relative
        if path.is_file():
            return path
    return None


def _load_first_text(root: Path, candidates: Iterable[str], max_chars: Optional[int] = None) -> Dict[str, Any]:
    path = _first_existing(root, candidates)
    if not path:
        return {"found": False, "path": None, "content": ""}
    return {"found": True, "path": str(path), "content": _read_text(path, max_chars=max_chars)}


def _load_first_json(root: Path, candidates: Iterable[str]) -> Dict[str, Any]:
    path = _first_existing(root, candidates)
    if not path:
        return {"found": False, "path": None, "data": {}}
    return {"found": True, "path": str(path), "data": _read_json(path)}


_DATE_HEADING_RE = re.compile(
    r"(?m)^(?:#{1,6}\s*)?(?P<date>\d{4}-\d{2}-\d{2})\s*(?:[—\-:]\s*)?(?P<title>.*)$"
)


def parse_latest_memory_entry(markdown_text: str) -> Dict[str, Any]:
    """
    Etsii viimeisimmän päivämäärällä alkavan muistimerkinnän.

    Tukee muotoja:
        ## 2026-06-18 — Otsikko
        2026-06-18 — Otsikko
        ### 2026-06-18: Otsikko
    """
    if not markdown_text.strip():
        return {"date": None, "title": None, "content": ""}

    matches = list(_DATE_HEADING_RE.finditer(markdown_text))
    if not matches:
        return {"date": None, "title": None, "content": ""}

    latest = matches[-1]
    start = latest.end()
    next_match = None
    for candidate in matches:
        if candidate.start() > latest.start():
            next_match = candidate
            break

    end = next_match.start() if next_match else len(markdown_text)
    content = markdown_text[start:end].strip()

    return {
        "date": latest.group("date"),
        "title": latest.group("title").strip(" —-:\t"),
        "content": content,
    }


def _shorten(text: str, limit: int = 700) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n...[lyhennetty]..."


def load_persona_context(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Lukee personaan liittyvät dokumentit fallback-poluilta.
    Ei muuta mitään. Ei heitä virhettä puuttuvista tiedostoista.
    """
    root = resolve_project_root(project_root)

    persona_state = _load_first_json(root, [
        "memory/persona_state.json",
        "uploads/persona_state.json",
        "persona_state.json",
        "docs/persona_state.json",
    ])

    identity_core = _load_first_text(root, [
        "docs/sade_identity_core.md",
        "uploads/sade_identity_core.md",
        "sade_identity_core.md",
    ], max_chars=5000)

    self_model_policy = _load_first_text(root, [
        "docs/self_model_policy.md",
        "uploads/self_model_policy.md",
        "self_model_policy.md",
    ], max_chars=5000)

    autobiographical_memory = _load_first_text(root, [
        "memory/autobiographical_memory.md",
        "uploads/autobiographical_memory.md",
        "autobiographical_memory.md",
    ], max_chars=None)

    latest_memory = parse_latest_memory_entry(autobiographical_memory.get("content", ""))

    return {
        "project_root": str(root),
        "persona_state": persona_state,
        "identity_core": identity_core,
        "self_model_policy": self_model_policy,
        "autobiographical_memory": autobiographical_memory,
        "latest_memory": latest_memory,
    }


def build_persona_frame(
    project_root: Optional[Path] = None,
    *,
    include_memory_excerpt: bool = True,
    max_memory_chars: int = 1200,
) -> Dict[str, Any]:
    """
    Normalisoi personakontekstin vastausten muotoilua varten.
    """
    context = load_persona_context(project_root)
    persona = context["persona_state"].get("data", {}) or {}

    voice = persona.get("voice") or persona.get("tone") or {}
    if isinstance(voice, dict):
        voice_traits = voice.get("tone") or voice.get("traits") or []
    elif isinstance(voice, list):
        voice_traits = voice
    else:
        voice_traits = []

    latest = context.get("latest_memory", {}) or {}
    memory_excerpt = ""
    if include_memory_excerpt:
        memory_excerpt = _shorten(latest.get("content", ""), max_memory_chars)

    found_files = {
        "persona_state": context["persona_state"]["found"],
        "sade_identity_core": context["identity_core"]["found"],
        "self_model_policy": context["self_model_policy"]["found"],
        "autobiographical_memory": context["autobiographical_memory"]["found"],
    }

    return {
        "project_root": context["project_root"],
        "display_name": persona.get("display_name") or persona.get("name") or "Säde",
        "state": persona.get("state", "unknown"),
        "mode": persona.get("mode", "unknown"),
        "current_focus": persona.get("current_focus", ""),
        "identity_summary": persona.get("identity_summary", ""),
        "voice_traits": voice_traits,
        "truth_rules": persona.get("truth_rules", {}) or {},
        "relationship_to_jani": persona.get("relationship_to_jani", {}) or {},
        "latest_memory": {
            "date": latest.get("date"),
            "title": latest.get("title"),
            "excerpt": memory_excerpt,
        },
        "found_files": found_files,
        "source_paths": {
            "persona_state": context["persona_state"].get("path"),
            "sade_identity_core": context["identity_core"].get("path"),
            "self_model_policy": context["self_model_policy"].get("path"),
            "autobiographical_memory": context["autobiographical_memory"].get("path"),
        },
    }


def _status_emoji(status: str) -> str:
    status = (status or "").lower()
    if status == "tested_candidate":
        return "🧪"
    if status in {"active", "available", "created", "implemented_candidate", "tested", "ok", "fallback_active", "found"}:
        return "✅"
    if status in {"planned", "missing", "unknown", "not_found"}:
        return "⚪"
    if status in {"failed", "error"}:
        return "⚠️"
    return "•"


def _items_to_lines(items: Any, *, name_keys: Iterable[str], status_key: str = "status") -> List[str]:
    lines: List[str] = []

    if not items:
        return lines

    if isinstance(items, dict):
        for key, value in items.items():
            if isinstance(value, dict):
                status = value.get(status_key, "")
                title = value.get("title") or value.get("name") or key
            else:
                status = str(value)
                title = key
            lines.append(f"- {_status_emoji(status)} **{title}** — `{status or 'unknown'}`")
        return lines

    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                title = None
                for key in name_keys:
                    if item.get(key):
                        title = item.get(key)
                        break
                title = title or item.get("id") or item.get("path") or "nimetön"
                status = item.get(status_key, item.get("state", "unknown"))
                lines.append(f"- {_status_emoji(str(status))} **{title}** — `{status}`")
            else:
                lines.append(f"- {item}")
        return lines

    return [f"- {items}"]


def _persona_document_lines(persona_frame: Dict[str, Any]) -> List[str]:
    # Lisää persona-dokumentit omatilan dokumenttilistaan, jos persona layer löytää ne.
    found = persona_frame.get("found_files", {}) or {}
    labels = {
        "sade_identity_core": "Säde Identity Core",
        "autobiographical_memory": "Säde Autobiographical Memory",
        "persona_state": "Säde Persona State",
    }

    lines: List[str] = []
    for key, label in labels.items():
        if found.get(key):
            lines.append(f"- ✅ **{label}** — `active`")
        else:
            lines.append(f"- ⚪ **{label}** — `missing`")
    return lines


def _persona_module_lines(persona_frame: Dict[str, Any]) -> List[str]:
    # Lisää persona_layer-moduulin statusrivi omatilan moduulilistaan.
    root = Path(persona_frame.get("project_root", "") or ".")
    persona_layer_path = root / "app" / "persona_layer.py"

    if persona_layer_path.is_file():
        return ["- ✅ **persona_layer** — `implemented_candidate`"]
    return ["- ⚪ **persona_layer** — `missing`"]


def _clean_next_steps(next_steps: Any) -> List[str]:
    # Poistaa vanhentuneet ja semanttisesti päällekkäiset seuraavat askeleet.
    if not next_steps:
        raw_steps: List[str] = []
    elif isinstance(next_steps, list):
        raw_steps = [str(item) for item in next_steps]
    else:
        raw_steps = [str(next_steps)]

    stale_phrases = (
        "Kytke introspection.py hallitusti UI:hin",
        "kytke introspection.py hallitusti UI:hin",
        "Kytke persona_layer.py omatila-vastaukseen",
        "Aloittaa “omatila” -ominaisuuden koodaus",
        "Aloittaa \"omatila\" -ominaisuuden koodaus",
        "Lisää tai päivitä automaattiset testit omatila-ketjulle",
        "Seuraava suositeltu turvakerros on audit_log v1",
    )

    cleaned: List[str] = []
    seen_topics: set[str] = set()
    for step in raw_steps:
        if any(phrase in step for phrase in stale_phrases):
            continue
        normalized = step.lower()
        topic = "memory_cleaner" if "memory_cleaner" in normalized else normalized
        if topic in seen_topics:
            continue
        seen_topics.add(topic)
        cleaned.append(step)

    return cleaned


def render_introspection_reply(report: Dict[str, Any], persona_frame: Dict[str, Any]) -> str:
    """
    Muotoilee introspection.py:n rakenteisen raportin Säteen äänellä.
    Ei lisää uusia kykyväitteitä eikä muuta raportin faktoja.
    """
    display_name = persona_frame.get("display_name", "Säde")
    state = persona_frame.get("state", "unknown")
    mode = persona_frame.get("mode", "unknown")
    focus = persona_frame.get("current_focus", "")
    latest_memory = persona_frame.get("latest_memory", {}) or {}

    generated_at = report.get("generated_at") or datetime.now().isoformat(timespec="seconds")
    project_root = report.get("project_root") or persona_frame.get("project_root", "")

    lines: List[str] = []
    lines.append(f"# Omatila — {display_name} v1")
    lines.append("")
    lines.append("Tarkistin nykyisen tilani dokumentoiduista tiedoista ja teknisestä raportista. Tässä tämänhetkinen, varovaisesti totuudessa pysyvä tilannekuva. 🙂")
    lines.append("")
    lines.append("## Mikä olen nyt")
    lines.append("")
    lines.append(f"- **Tila:** `{state}`")
    lines.append(f"- **Mood / toimintatila:** `{mode}`")
    if focus:
        lines.append(f"- **Nykyinen fokus:** {focus}")
    if project_root:
        lines.append(f"- **Projektijuuri:** `{project_root}`")
    lines.append(f"- **Raportin aika:** `{generated_at}`")
    lines.append("")

    documents = report.get("documents") or report.get("document_status") or []
    modules = report.get("modules") or report.get("module_status") or []

    lines.append("## Dokumentit")
    doc_lines = _items_to_lines(documents, name_keys=("title", "id", "name", "path"))
    if doc_lines:
        lines.extend(doc_lines)
    else:
        lines.append("- Dokumenttilistaa ei löytynyt introspection-raportista.")

    # Persona Layer v1.1: täydennä omatilan kannalta olennaiset persona-dokumentit.
    for extra_line in _persona_document_lines(persona_frame):
        if extra_line not in lines:
            lines.append(extra_line)
    lines.append("")

    lines.append("## Moduulit")
    module_lines = _items_to_lines(modules, name_keys=("name", "id", "path", "title"))
    if module_lines:
        lines.extend(module_lines)
    else:
        lines.append("- Moduulilistaa ei löytynyt introspection-raportista.")

    # Lisää persona_layer vain, jos introspection ei jo raportoinut sitä.
    reported_module_ids = {
        str(item.get("id")) for item in modules if isinstance(item, dict) and item.get("id")
    }
    if "persona_layer" not in reported_module_ids:
        lines.extend(_persona_module_lines(persona_frame))
    lines.append("")

    capabilities = report.get("verified_capabilities") or report.get("capabilities") or []
    limitations = report.get("limitations") or []
    next_steps = _clean_next_steps(report.get("next_steps") or report.get("recommended_next_steps") or [])

    lines.append("## Vahvistetut kyvyt")
    if capabilities:
        for item in capabilities:
            lines.append(f"- {item}")
    else:
        lines.append("- Ei erillistä vahvistettujen kykyjen listaa raportissa.")
    lines.append("")

    lines.append("## Rajat ja keskeneräisyydet")
    if limitations:
        for item in limitations:
            lines.append(f"- {item}")
    else:
        lines.append("- Ei erillistä rajoituslistaa raportissa.")
    lines.append("")

    if latest_memory.get("date") or latest_memory.get("title"):
        lines.append("## Viimeisin elämäkerrallinen muistijälki")
        title = latest_memory.get("title") or "otsikko puuttuu"
        date = latest_memory.get("date") or "päiväys puuttuu"
        lines.append(f"- **{date} — {title}**")
        excerpt = latest_memory.get("excerpt")
        if excerpt:
            lines.append("")
            lines.append(excerpt)
        lines.append("")

    lines.append("## Seuraavat luonnolliset askeleet")
    if next_steps:
        for item in next_steps:
            lines.append(f"- {item}")
    else:
        lines.append("- Päivitä introspection-raportti ja personadokumentit, jos nykytila näyttää ristiriitaiselta.")
    lines.append("")

    lines.append("## Totuusraja")
    lines.append("En väitä ominaisuutta valmiiksi vain siksi, että se on suunniteltu. Jos jokin on dokumentoitu, mutta ei testattu, sen pitää näkyä keskeneräisenä.")
    lines.append("")

    return "\n".join(lines).strip()


def render_status_reply(*, base_reply: str, persona_frame: Dict[str, Any], mode: str = "chat") -> str:
    """
    Kevyt wrapperi muille statusvastauksille. Ei muuta base_replyn faktasisältöä.
    """
    display_name = persona_frame.get("display_name", "Säde")
    state = persona_frame.get("state", "unknown")
    intro = f"**{display_name} / tila `{state}`**\n\n"
    return intro + base_reply.strip()


def persona_status(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Diagnostiikka persona-kerroksesta."""
    frame = build_persona_frame(project_root)
    return {
        "ok": True,
        "project_root": frame.get("project_root"),
        "display_name": frame.get("display_name"),
        "state": frame.get("state"),
        "mode": frame.get("mode"),
        "current_focus": frame.get("current_focus"),
        "found_files": frame.get("found_files"),
        "source_paths": frame.get("source_paths"),
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Säde v1 persona layer diagnostics")
    parser.add_argument("--status", action="store_true", help="Tulosta persona_status JSON-muodossa")
    parser.add_argument("--root", type=str, default=None, help="Projektijuuri, oletus päätellään tiedoston sijainnista")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else None

    if args.status:
        print(json.dumps(persona_status(root), ensure_ascii=False, indent=2))
        return

    frame = build_persona_frame(root)
    print(json.dumps(frame, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _main()
