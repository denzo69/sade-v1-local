
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
import re


def _norm(text: str) -> str:
    text = str(text or "").strip().lower()
    text = text.replace("ä", "a").replace("ö", "o")
    return re.sub(r"\s+", " ", text)


def _app_path(project_path: Any) -> Path:
    path = Path(project_path).resolve()

    if path.name.lower() == "app":
        return path

    candidate = path / "app"

    if candidate.exists() and candidate.is_dir():
        return candidate

    return path


def try_handle_dev_command(project_path: Any, message: str) -> Optional[str]:
    msg = _norm(message)

    if msg in {
        "tee koodikartta",
        "luo koodikartta",
        "paivita koodikartta",
        "dev map",
        "codebase map",
        "koodikartta",
    }:
        from app.codebase_map import build_codebase_map

        result = build_codebase_map(_app_path(project_path), include_snippets=False)

        return "\\n".join([
            "Koodikartta luotu Dev Modella. ✅",
            "",
            f"Tiedostot: {result.get('file_count', 0)}",
            f"Reitit: {result.get('route_count', 0)}",
            f"Funktiot: {result.get('function_count', 0)}",
            f"Luokat: {result.get('class_count', 0)}",
            f"Polku: `{result.get('map_path', '')}`",
        ])

    if msg in {
        "nayta koodikartta",
        "lue koodikartta",
        "koodikartan tila",
        "dev status",
        "dev tila",
    }:
        from app.codebase_map import read_codebase_map

        result = read_codebase_map(_app_path(project_path))

        if not result.get("ok"):
            return result.get("message", "Koodikarttaa ei löytynyt.")

        return "\\n".join([
            "Koodikartta löytyy. ✅",
            "",
            f"Tiedostot: {result.get('file_count', 0)}",
            f"Reitit: {result.get('route_count', 0)}",
            f"Funktiot: {result.get('function_count', 0)}",
            f"Luokat: {result.get('class_count', 0)}",
            f"Polku: `{result.get('map_path', '')}`",
        ])

    prefixes = [
        "etsi koodista ",
        "hae koodista ",
        "etsi koodikartasta ",
        "hae koodikartasta ",
        "dev find ",
    ]

    for prefix in prefixes:
        if msg.startswith(prefix):
            query = msg[len(prefix):].strip()

            if not query:
                return "Anna hakusana, esim. `etsi koodista rag_search`."

            from app.codebase_map import find_in_codebase_map

            result = find_in_codebase_map(_app_path(project_path), query, limit=10)

            if not result.get("ok"):
                return result.get("message", "Koodikarttahaku epäonnistui.")

            items = result.get("results") or []

            if not items:
                return f"En löytänyt koodikartasta osumia haulle `{query}`."

            lines = [f"Löysin koodikartasta {len(items)} osumaa haulle `{query}`:", ""]

            for i, item in enumerate(items[:10], 1):
                path = item.get("path") or item.get("file") or "tuntematon"
                lines.append(f"{i}. `{path}`")

                summary = item.get("summary") or item.get("matched") or item.get("matches")

                if summary:
                    lines.append(str(summary)[:700])

                lines.append("")

            return "\\n".join(lines).strip()

    return None
