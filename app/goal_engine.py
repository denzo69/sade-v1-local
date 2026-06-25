from __future__ import annotations

"""Säde v1 — Goal Engine v1.

Read-only-moduuli oppimisen ja kehityksen tilan tarkistamiseen.
Ei muuta tiedostoja eikä anna lupaa muutoksiin.
"""

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ComponentStatus:
    id: str
    label: str
    path: str
    status: str
    role: str


@dataclass
class GoalRecommendation:
    id: str
    title: str
    reason: str
    risk_level: str
    status: str
    suggested_files: List[str]
    test_commands: List[str]
    requires_jani_approval: bool


def resolve_project_root(project_root: Optional[Path] = None) -> Path:
    if project_root is None:
        return Path(__file__).resolve().parent.parent
    root = Path(project_root).resolve()
    return root.parent if root.name.lower() == "app" else root


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_text(path: Path, tail: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-tail:] if tail and len(text) > tail else text


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def file_status(root: Path, rel: str, missing_status: str = "planned", test_rel: Optional[str] = None) -> str:
    if not (root / rel).exists():
        return missing_status
    return "tested_candidate" if test_rel and (root / test_rel).exists() else "implemented_candidate"


def is_available(status: str) -> bool:
    return status in {"implemented_candidate", "tested_candidate", "tested", "active"}


def collect_components(root: Path) -> List[ComponentStatus]:
    return [
        ComponentStatus("development_roadmap", "Development Roadmap", "docs/development_roadmap.md", file_status(root, "docs/development_roadmap.md"), "Kehityskartta ja vaiheistus."),
        ComponentStatus("code_rewrite_protocol", "Code Rewrite Protocol", "docs/code_rewrite_protocol.md", file_status(root, "docs/code_rewrite_protocol.md"), "Turvattu koodimuutosprosessi."),
        ComponentStatus("audit_log", "Audit Log", "app/audit_log.py", file_status(root, "app/audit_log.py", test_rel="tests/test_audit_log.py"), "Tekninen tapahtumaloki."),
        ComponentStatus("web_search", "Web Search Tool", "app/web_search.py", file_status(root, "app/web_search.py", test_rel="tests/test_web_search.py"), "Hallittu verkkohaku faktakysymyksiin."),
        ComponentStatus("finnish_language_pack", "Finnish Language Pack", "app/language_pack.py", file_status(root, "app/language_pack.py", test_rel="tests/test_language_pack.py"), "Suomen kieli- ja sanastokonteksti."),
        ComponentStatus("learning_feedback", "Learning Feedback Memory", "app/learning_feedback.py", file_status(root, "app/learning_feedback.py", test_rel="tests/test_learning_feedback.py"), "Janin korjausten tallennus oppiesimerkeiksi."),
        ComponentStatus("goal_engine", "Goal Engine", "app/goal_engine.py", file_status(root, "app/goal_engine.py", test_rel="tests/test_goal_engine.py"), "Kehityksen ja oppimistilan read-only-ohjain."),
        ComponentStatus("task_state", "Task State", "memory/task_state.json", file_status(root, "memory/task_state.json"), "Keskeneräisten tehtävien tila."),
        ComponentStatus("tests", "Automated Tests", "tests", "implemented_candidate" if (root / "tests").exists() else "planned", "Automaattiset pytest-testit."),
        ComponentStatus("memory_cleaner", "Memory Cleaner", "app/memory_cleaner.py", file_status(root, "app/memory_cleaner.py", "missing", "tests/test_memory_cleaner.py"), "Muistien siivous; ei aktiivinen ilman lupaa."),
    ]


def by_id(components: List[ComponentStatus]) -> Dict[str, ComponentStatus]:
    return {item.id: item for item in components}


def emoji(status: str) -> str:
    return {"implemented_candidate": "✅", "tested_candidate": "🧪", "tested": "✅", "active": "✅", "planned": "⚪", "missing": "⚪", "prepared": "🟡", "in_progress": "🟡"}.get(status, "•")


def latest_memory_excerpt(root: Path) -> str:
    for rel in ["memory/autobiographical_memory.md", "uploads/autobiographical_memory.md"]:
        text = read_text(root / rel, 14000)
        if text:
            headings = list(re.finditer(r"^##\s+(.+)$", text, flags=re.MULTILINE))
            if headings:
                return text[headings[-1].start():].strip()[:1600]
            return text.strip()[-1600:]
    return "Ei viimeisintä elämäkerrallista muistijälkeä löytynyt."


def learning_findings(root: Path, components: List[ComponentStatus]) -> List[str]:
    c = by_id(components)
    findings: List[str] = []
    findings.append("Kehityskartta on olemassa ja ohjaa etenemistä vaiheittain." if c["development_roadmap"].status == "implemented_candidate" else "Kehityskartta ei vielä näy toteutettuna dokumenttina.")
    findings.append("Verkkohakutyökalu on olemassa ja siihen kohdistuu automaattinen testi." if is_available(c["web_search"].status) else "Verkkohakutyökalu puuttuu vielä tai sitä ei ole asennettu tähän projektiin.")
    if is_available(c["finnish_language_pack"].status):
        findings.append("Suomen kielipaketti näyttää olevan kytketty päävastauksen muodostukseen." if "build_language_context" in read_text(root / "app/main.py") else "Suomen kielipaketti on olemassa, mutta sitä ei vielä näy kytkettynä päävastauksen muodostukseen.")
    else:
        findings.append("Suomen kielipaketti puuttuu tai sitä ei ole asennettu tähän projektiin.")
    findings.append("Oppimispalautteen tallennus on olemassa ja siihen kohdistuu automaattinen testi." if is_available(c["learning_feedback"].status) else "Janin korjauksista oppiva palautemuisti puuttuu vielä. Tämä on itseoppimisen seuraava tärkeä kerros.")
    if is_available(c["audit_log"].status):
        main_text = read_text(root / "app/main.py")
        findings.append("Audit Log v1 on olemassa ja keskeiset API-, kirjoitus-, tehtävä- ja työkalutoiminnot on kytketty keskitettyyn auditointiin." if "write_audit_event" in main_text and "tools_router_run" in main_text else "Audit log on olemassa, mutta keskitettyä integraatiota ei vielä havaittu.")
    else:
        findings.append("Audit log puuttuu tai sitä ei ole asennettu tähän projektiin.")
    if c["memory_cleaner"].status == "missing":
        findings.append("Memory cleaner on puuttuva eikä automaattinen muistienpoisto ole aktiivinen. Tämä on turvallinen nykytila.")
    return findings


def next_recommendation(root: Path, components: List[ComponentStatus]) -> GoalRecommendation:
    c = by_id(components)
    if not is_available(c["web_search"].status):
        return GoalRecommendation("web_search_tool_v1", "Web Search Tool v1", "Faktakysymykset tarvitsevat lähteitä, jotta Säde ei arvaa tai keksi tietoa.", "controlled_write", "recommended", ["app/web_search.py", "docs/web_search_policy.md", "data/web_source_registry_fi.json", "app/tool_router.py"], ["python app\\web_search.py"], True)
    if not is_available(c["learning_feedback"].status):
        return GoalRecommendation("learning_feedback_memory_v1", "Learning Feedback Memory v1", "Säde tarvitsee mekanismin, jolla Janin korjaukset muuttuvat oppiesimerkeiksi eikä samoja virheitä toisteta.", "controlled_write", "recommended", ["app/learning_feedback.py", "data/language_incidents.jsonl", "data/correction_examples.jsonl", "docs/learning_feedback_policy.md", "app/tool_router.py"], ["python app\\learning_feedback.py"], True)
    if is_available(c["finnish_language_pack"].status) and "build_language_context" not in read_text(root / "app/main.py"):
        return GoalRecommendation("language_pack_llm_integration_v1", "Finnish Language Pack LLM Integration v1", "Kielipaketti on olemassa, mutta sitä ei vielä näy syötettävän mallille ennen vastausta.", "controlled_write", "recommended", ["app/main.py", "app/language_pack.py"], ["python app\\language_pack.py"], True)
    if is_available(c["audit_log"].status) and "write_audit_event" not in read_text(root / "app/main.py"):
        return GoalRecommendation("audit_log_tool_router_integration_v1", "Audit Log Tool Router Integration v1", "Audit log on olemassa, mutta työkalureitit eivät välttämättä vielä kirjaudu automaattisesti.", "controlled_write", "recommended", ["app/tool_router.py", "app/audit_log.py"], ["python app\\audit_log.py"], True)
    if c["task_state"].status != "implemented_candidate":
        return GoalRecommendation("task_state_v1", "Task State v1", "Säde tarvitsee tiedon siitä, mikä työ on kesken ja mikä on seuraava askel.", "controlled_write", "recommended", ["memory/task_state.json", "app/task_state.py", "docs/task_state_policy.md"], ["python app\\task_state.py"], True)
    return GoalRecommendation("automated_tests_v1", "Automated Tests v1", "Kun perusmoduulit ovat olemassa, seuraava laatuaskel on testata ne automaattisesti.", "controlled_write", "recommended", ["tests/test_tool_router.py", "tests/test_goal_engine.py", "tests/test_language_pack.py"], ["python -m pytest"], True)


def build_goal_status(project_root: Optional[Path] = None) -> Dict[str, Any]:
    root = resolve_project_root(project_root)
    comps = collect_components(root)
    rec = next_recommendation(root, comps)
    persona = read_json(root / "memory/persona_state.json") or read_json(root / "uploads/persona_state.json")
    return {"ok": True, "time": now_iso(), "project_root": str(root), "mode": "read_only_goal_status", "components": [asdict(i) for i in comps], "learning_findings": learning_findings(root, comps), "recent_memory": latest_memory_excerpt(root), "recommendation": asdict(rec), "persona_development": persona.get("development", {}), "truth_boundary": ["Goal Engine v1 ei muuta tiedostoja.", "Tiedoston olemassaolo ei tarkoita testattua ominaisuutta.", "Suositus ei ole hyväksyntä eikä toteutus."]}


def build_learning_status_reply(project_root: Optional[Path] = None) -> str:
    status = build_goal_status(project_root)
    comps = [ComponentStatus(**i) for i in status["components"]]
    rec = status["recommendation"]
    lines = ["# Oppimistila — Säde v1", "", "Tarkistin kehityksen ja oppimisen tilan dokumentoiduista tiedoista. Tämä on read-only-raportti eikä muuta tiedostoja. 🙂", "", "## Nykyinen oppimistila", ""]
    lines += [f"- {x}" for x in status["learning_findings"]]
    lines += ["", "## Keskeiset osat", ""]
    lines += [f"- {emoji(i.status)} **{i.label}** — `{i.status}` — `{i.path}`" for i in comps]
    lines += ["", "## Seuraava suositeltu kehitysaskel", "", f"**{rec['title']}**", "", f"- **ID:** `{rec['id']}`", f"- **Syy:** {rec['reason']}", f"- **Riskitaso:** `{rec['risk_level']}`", f"- **Vaatii Janin hyväksynnän:** {'kyllä' if rec['requires_jani_approval'] else 'ei'}", "", "### Mahdolliset tiedostot"]
    lines += [f"- `{x}`" for x in rec.get("suggested_files", [])]
    lines += ["", "### Testit"]
    lines += [f"- `{x}`" for x in rec.get("test_commands", [])]
    lines += ["", "## Viimeisin oppimiseen liittyvä muistijälki", "", status["recent_memory"], "", "## Totuusraja", ""]
    lines += [f"- {x}" for x in status["truth_boundary"]]
    return "\n".join(lines).strip()


def build_next_goal_reply(project_root: Optional[Path] = None) -> str:
    status = build_goal_status(project_root)
    rec = status["recommendation"]
    lines = ["# Seuraava kehitysaskel — Säde v1", "", f"Seuraavaksi suosittelen: **{rec['title']}**", "", f"**Miksi:** {rec['reason']}", "", f"- ID: `{rec['id']}`", f"- Tila: `{rec['status']}`", f"- Riskitaso: `{rec['risk_level']}`", f"- Vaatii Janin hyväksynnän: {'kyllä' if rec['requires_jani_approval'] else 'ei'}", "", "## Tiedostot"]
    lines += [f"- `{x}`" for x in rec.get("suggested_files", [])]
    lines += ["", "## Testit"]
    lines += [f"- `{x}`" for x in rec.get("test_commands", [])]
    lines += ["", "## Totuusraja", "", "Tämä on suositus, ei toteutus. Muutoksia ei tehdä ilman Janin hyväksyntää."]
    return "\n".join(lines).strip()


def is_goal_engine_request(message: str) -> bool:
    text = " ".join((message or "").lower().split())
    return any(t in text for t in ["oppimisen tila", "tila oppimisen suhteen", "mitä olet oppinut", "mitä opit", "mikä on seuraava kehitysaskel", "mitä rakennetaan seuraavaksi", "mitä seuraavaksi rakennetaan", "kehityksen tila", "roadmap tila", "tavoitetila", "goal engine"])


def route_goal_engine_request(project_root: Optional[Path], message: str) -> Dict[str, Any]:
    text = " ".join((message or "").lower().split())
    reply = build_next_goal_reply(project_root) if any(t in text for t in ["mikä on seuraava", "mitä rakennetaan seuraavaksi", "mitä seuraavaksi rakennetaan"]) else build_learning_status_reply(project_root)
    return {"handled": True, "tool": "goal_engine", "result": build_goal_status(project_root), "reply": reply}


if __name__ == "__main__":
    print(build_learning_status_reply())
