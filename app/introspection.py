from __future__ import annotations

"""
Säde v1 Introspection Module

Tarkoitus:
- Lukee projektin nykytilaa turvallisesti.
- Ei muuta tiedostoja.
- Ei käynnistä automaatioita.
- Ei väitä suunniteltuja moduuleja toteutetuiksi.
- Palauttaa rehellisen tilaraportin dokumenteista, moduuleista ja seuraavista askelista.

Käyttö komentoriviltä:
    python app/introspection.py
    python app/introspection.py --format markdown
    python app/introspection.py --format json
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import argparse
import hashlib
import json
import re

try:
    from app.audit_log import audit_status, read_audit_log
except ImportError:  # Suora ajo: python app/introspection.py
    from audit_log import audit_status, read_audit_log


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class FileStatus:
    id: str
    title: str
    canonical_path: str
    fallback_path: Optional[str]
    status: str
    active_path: Optional[str]
    exists_canonical: bool
    exists_fallback: bool
    size_bytes: Optional[int]
    modified: Optional[str]
    sha256_12: Optional[str]
    note: str


@dataclass
class ModuleStatus:
    id: str
    path: str
    expected_role: str
    status: str
    exists: bool
    referenced_by: List[str]
    size_bytes: Optional[int]
    modified: Optional[str]
    note: str


DOCUMENTS: List[Dict[str, Optional[str]]] = [
    {
        "id": "project_inventory",
        "title": "Säde v1 Project Inventory",
        "canonical_path": "docs/project_inventory.md",
        "fallback_path": "uploads/project_inventory.md",
    },
    {
        "id": "document_registry",
        "title": "Säde v1 Document Registry",
        "canonical_path": "docs/document_registry.md",
        "fallback_path": "uploads/document_registry.md",
    },
    {
        "id": "memory_policy",
        "title": "Säde Memory Policy",
        "canonical_path": "docs/memory_policy.md",
        "fallback_path": "uploads/memory_policy.md",
    },
    {
        "id": "rag_source_policy",
        "title": "Säde RAG Source Policy",
        "canonical_path": "docs/rag_source_policy.md",
        "fallback_path": "uploads/rag_source_policy.md",
    },
    {
        "id": "tool_permission_policy",
        "title": "Säde Tool Permission Policy",
        "canonical_path": "docs/tool_permission_policy.md",
        "fallback_path": "uploads/tool_permission_policy.md",
    },
    {
        "id": "guardrails",
        "title": "Säde Guardrails",
        "canonical_path": "docs/guardrails.md",
        "fallback_path": "uploads/guardrails.md",
    },
    {
        "id": "sade_operating_manual",
        "title": "Säde Operating Manual",
        "canonical_path": "docs/sade_operating_manual.md",
        "fallback_path": "uploads/sade_operating_manual.md",
    },
    {
        "id": "self_model_policy",
        "title": "Säde Self Model Policy",
        "canonical_path": "docs/self_model_policy.md",
        "fallback_path": "uploads/self_model_policy.md",
    },
    {
        "id": "sade_identity_core",
        "title": "Säde Identity Core",
        "canonical_path": "docs/sade_identity_core.md",
        "fallback_path": "uploads/sade_identity_core.md",
    },
    {
        "id": "autobiographical_memory",
        "title": "Säde Autobiographical Memory",
        "canonical_path": "memory/autobiographical_memory.md",
        "fallback_path": "uploads/autobiographical_memory.md",
    },
    {
        "id": "persona_state",
        "title": "Säde Persona State",
        "canonical_path": "memory/persona_state.json",
        "fallback_path": "uploads/persona_state.json",
    },
    {
        "id": "development_roadmap",
        "title": "Säde Development Roadmap",
        "canonical_path": "docs/development_roadmap.md",
        "fallback_path": "uploads/development_roadmap.md",
    },
    {
        "id": "code_rewrite_protocol",
        "title": "Säde Code Rewrite Protocol",
        "canonical_path": "docs/code_rewrite_protocol.md",
        "fallback_path": "uploads/code_rewrite_protocol.md",
    },
    {
        "id": "audit_log_policy",
        "title": "Säde Audit Log Policy",
        "canonical_path": "docs/audit_log_policy.md",
        "fallback_path": "uploads/audit_log_policy.md",
    },
    {
        "id": "goal_engine_policy",
        "title": "Säde Goal Engine Policy",
        "canonical_path": "docs/goal_engine_policy.md",
        "fallback_path": "uploads/goal_engine_policy.md",
    },
    {
        "id": "web_search_policy",
        "title": "Säde Web Search Policy",
        "canonical_path": "docs/web_search_policy.md",
        "fallback_path": "uploads/web_search_policy.md",
    },
    {
        "id": "finnish_language_pack",
        "title": "Säde Finnish Language Pack",
        "canonical_path": "docs/finnish_language_pack.md",
        "fallback_path": "uploads/finnish_language_pack.md",
    },
]

MODULES: List[Dict[str, str]] = [
    {
        "id": "main",
        "path": "app/main.py",
        "expected_role": "FastAPI-sovelluksen päämoduuli.",
    },
    {
        "id": "rag_engine",
        "path": "app/rag_engine.py",
        "expected_role": "RAG-haun ja lähteiden hakulogiikan moduuli.",
    },
    {
        "id": "semantic_memory",
        "path": "app/semantic_memory.py",
        "expected_role": "Semanttisen muistin moduuli.",
    },
    {
        "id": "tool_router",
        "path": "app/tool_router.py",
        "expected_role": "Työkalupyyntöjen reititin.",
    },
    {
        "id": "tools",
        "path": "app/tools.py",
        "expected_role": "Turvallinen työkalukerros tiedostojen lukemiseen/listaukseen/kirjoitukseen.",
    },
    {
        "id": "introspection",
        "path": "app/introspection.py",
        "expected_role": "Lukevan omatila-/tilaraportin moduuli.",
    },
    {
        "id": "persona_layer",
        "path": "app/persona_layer.py",
        "expected_role": "Muotoilee omatila- ja statusraportit Säteen dokumentoidulla äänellä.",
    },
    {
        "id": "goal_engine",
        "path": "app/goal_engine.py",
        "expected_role": "Lukee kehityskartan ja antaa oppimisen sekä seuraavan kehitysaskeleen read-only-raportin.",
    },
    {
        "id": "web_search",
        "path": "app/web_search.py",
        "expected_role": "Hallittu verkkohakutyökalu faktakysymyksiä varten.",
    },
    {
        "id": "audit_log",
        "path": "app/audit_log.py",
        "expected_role": "Tekninen tapahtumaloki muutosten ja työkalukutsujen jäljitettävyyteen.",
    },
    {
        "id": "language_pack",
        "path": "app/language_pack.py",
        "expected_role": "Suomen kieli- ja sanastokontekstin rakentaja.",
    },
    {
        "id": "learning_feedback",
        "path": "app/learning_feedback.py",
        "expected_role": "Suunniteltu oppimispalaute- ja virhepankkimoduuli Janin korjauksille.",
    },
    {
        "id": "memory_cleaner",
        "path": "app/memory_cleaner.py",
        "expected_role": "Suunniteltu muistihuollon moduuli. Ei saa väittää käytössä olevaksi ilman tiedostoa, kytkentää ja testiä.",
    },
]

REFERENCE_FILES = [
    "app/main.py",
    "app/tool_router.py",
    "app/tools.py",
    "app/rag_engine.py",
    "app/introspection.py",
    "app/persona_layer.py",
    "app/goal_engine.py",
    "app/web_search.py",
    "app/audit_log.py",
    "app/language_pack.py",
    "app/learning_feedback.py",
    "app/memory_cleaner.py",
]


def _safe_join(root: Path, relative_path: str) -> Path:
    """Palauttaa polun projektijuuren sisältä tai nostaa virheen."""
    candidate = (root / relative_path).resolve()
    root_resolved = root.resolve()

    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"Polku karkaa projektijuuren ulkopuolelle: {relative_path}") from exc

    return candidate


def _file_modified(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")


def _sha256_12(path: Path, max_bytes: int = 2_000_000) -> Optional[str]:
    """
    Laskee lyhyen SHA256-tunnisteen pienille/kohtuullisille tiedostoille.
    Ei lue suuria tiedostoja kokonaan muistiin.
    """
    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()
    read_bytes = 0

    with path.open("rb") as file:
        while True:
            chunk = file.read(65536)
            if not chunk:
                break
            read_bytes += len(chunk)
            if read_bytes > max_bytes:
                return "too_large"
            digest.update(chunk)

    return digest.hexdigest()[:12]


def _read_text_limited(path: Path, max_chars: int = 80_000) -> str:
    if not path.exists() or not path.is_file():
        return ""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    return text[:max_chars]


def _find_references(root: Path, module_id: str, module_path: str) -> List[str]:
    """
    Etsii kevyesti, viitataanko moduuliin päämoduuleissa.
    Tämä ei todista täydellistä runtime-integraatiota, mutta antaa varovaisen signaalin.
    """
    references: List[str] = []
    module_stem = Path(module_path).stem

    patterns = {
        module_id,
        module_stem,
        f"app.{module_stem}",
        f"from app.{module_stem}",
        f"import {module_stem}",
    }

    for relative in REFERENCE_FILES:
        ref_path = _safe_join(root, relative)
        if not ref_path.exists() or ref_path.as_posix().endswith(module_path):
            continue

        text = _read_text_limited(ref_path)
        if any(pattern in text for pattern in patterns):
            references.append(relative)

    return references


def _find_test_references(root: Path, module_id: str, module_path: str) -> List[str]:
    tests_path = root / "tests"
    if not tests_path.exists():
        return []
    module_stem = Path(module_path).stem
    references: List[str] = []
    for test_file in sorted(tests_path.glob("test_*.py")):
        text = _read_text_limited(test_file)
        if any(pattern in text for pattern in {module_id, module_stem, f"app.{module_stem}"}):
            references.append(str(test_file.relative_to(root)).replace("\\", "/"))
    return references


def inspect_tests(root: Path) -> Dict[str, Any]:
    tests_path = root / "tests"
    test_files = sorted(tests_path.glob("test_*.py")) if tests_path.exists() else []
    discovered: List[str] = []
    for test_file in test_files:
        text = _read_text_limited(test_file)
        for match in re.finditer(r"^def\s+(test_[A-Za-z0-9_]+)\s*\(", text, flags=re.MULTILINE):
            discovered.append(f"{test_file.name}::{match.group(1)}")
    return {
        "framework": "pytest",
        "test_files": [str(path.relative_to(root)).replace("\\", "/") for path in test_files],
        "discovered_test_count": len(discovered),
        "discovered_tests": discovered,
        "last_run_status": "not_executed_by_introspection",
        "note": "Introspection on read-only eikä käynnistä pytestiä. Testien olemassaolo ei yksin todista viimeisimmän ajon läpäisyä.",
    }


def inspect_ui(root: Path) -> Dict[str, Any]:
    ui_path = root / "app" / "templates" / "ui.html"
    text = _read_text_limited(ui_path, max_chars=250_000)
    tabs = re.findall(r'data-tab="([^"]+)"', text)
    return {
        "path": "app/templates/ui.html",
        "exists": ui_path.exists(),
        "language": "fi" if '<html lang="fi">' in text else "unknown",
        "chat_first": 'class="tab-panel active" id="panel-chat"' in text,
        "tabbed_workspace": len(tabs) >= 2,
        "tabs": tabs,
        "lazy_memory": "Muisti ladataan pyynnöstä." in text,
        "modified": _file_modified(ui_path),
    }


def recent_project_changes(root: Path, limit: int = 8) -> List[Dict[str, Any]]:
    candidates: List[Path] = []
    for pattern in ("app/*.py", "app/templates/*.html", "docs/*.md", "tests/test_*.py"):
        candidates.extend(path for path in root.glob(pattern) if path.is_file() and "backup" not in path.name.lower())
    latest = sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
    return [
        {
            "path": str(path.relative_to(root)).replace("\\", "/"),
            "modified": _file_modified(path),
            "sha256_12": _sha256_12(path),
        }
        for path in latest
    ]


def inspect_document(root: Path, doc: Dict[str, Optional[str]]) -> FileStatus:
    canonical_path = doc["canonical_path"] or ""
    fallback_path = doc.get("fallback_path")

    canonical = _safe_join(root, canonical_path)
    fallback = _safe_join(root, fallback_path) if fallback_path else None

    exists_canonical = canonical.exists() and canonical.is_file()
    exists_fallback = bool(fallback and fallback.exists() and fallback.is_file())

    if exists_canonical:
        active_path = canonical
        status = "active"
        note = "Canonical docs-versio löytyy."
    elif exists_fallback and fallback is not None:
        active_path = fallback
        status = "fallback_active"
        note = "Canonical docs-versio puuttuu tai ei ole luettavissa, mutta uploads-fallback löytyy."
    else:
        active_path = None
        status = "missing"
        note = "Dokumenttia ei löytynyt canonical- eikä fallback-polusta."

    return FileStatus(
        id=str(doc["id"]),
        title=str(doc["title"]),
        canonical_path=canonical_path,
        fallback_path=fallback_path,
        status=status,
        active_path=str(active_path.relative_to(root)).replace("\\", "/") if active_path else None,
        exists_canonical=exists_canonical,
        exists_fallback=exists_fallback,
        size_bytes=active_path.stat().st_size if active_path else None,
        modified=_file_modified(active_path) if active_path else None,
        sha256_12=_sha256_12(active_path) if active_path else None,
        note=note,
    )


def inspect_module(root: Path, module: Dict[str, str]) -> ModuleStatus:
    relative_path = module["path"]
    path = _safe_join(root, relative_path)
    exists = path.exists() and path.is_file()
    references = _find_references(root, module["id"], relative_path)
    test_references = _find_test_references(root, module["id"], relative_path)

    if not exists:
        status = "missing"
        note = "Tiedostoa ei löytynyt. Tätä ei saa väittää toteutetuksi."
    elif test_references:
        status = "tested_candidate"
        note = "Tiedosto löytyy ja siihen kohdistuu automaattinen testi. Introspection ei kuitenkaan aja testejä itse."
        references = references + test_references
    elif references:
        status = "implemented_candidate"
        note = "Tiedosto löytyy ja siihen viitataan muissa moduuleissa. Tämä ei vielä todista onnistunutta testiä."
    else:
        status = "created"
        note = "Tiedosto löytyy, mutta integraatioviitteitä ei havaittu päämoduuleissa."

    return ModuleStatus(
        id=module["id"],
        path=relative_path,
        expected_role=module["expected_role"],
        status=status,
        exists=exists,
        referenced_by=references,
        size_bytes=path.stat().st_size if exists else None,
        modified=_file_modified(path) if exists else None,
        note=note,
    )


def build_introspection_report(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Rakentaa lukevan tilaraportin.
    Ei kirjoita tiedostoja, ei käynnistä prosesseja, ei tee pysyviä muutoksia.
    """
    root = (project_root or PROJECT_ROOT).resolve()

    documents = [asdict(inspect_document(root, doc)) for doc in DOCUMENTS]
    modules = [asdict(inspect_module(root, module)) for module in MODULES]

    active_docs = [doc["id"] for doc in documents if doc["status"] in {"active", "fallback_active"}]
    missing_docs = [doc["id"] for doc in documents if doc["status"] == "missing"]

    created_or_better_modules = [
        module["id"]
        for module in modules
        if module["status"] in {"created", "implemented_candidate", "tested_candidate"}
    ]
    missing_modules = [module["id"] for module in modules if module["status"] == "missing"]

    limitations = [
        "Tämä raportti on lukutoiminto eikä muuta tiedostoja.",
        "implemented_candidate ei tarkoita testattua ominaisuutta.",
        "tested_candidate tarkoittaa testikytkentää, ei tässä raportissa ajettua pytest-tulosta.",
        "Suunniteltuja moduuleja ei saa väittää käytössä oleviksi.",
    ]

    next_steps: List[str] = []

    if "goal_engine" not in created_or_better_modules:
        next_steps.append("Lisää Goal Engine v1 oppimisen ja kehityksen read-only-raportointiin.")

    if "web_search" not in created_or_better_modules:
        next_steps.append("Lisää hallittu Web Search Tool v1, jotta faktakysymyksissä ei tarvitse arvata.")

    if "audit_log" not in created_or_better_modules:
        next_steps.append("Lisää audit_log v1 ennen riskialttiimpia automaatioita.")
    elif not audit_status(root).get("valid", False):
        next_steps.append("Tutki rikkoutunut audit-ketju ennen uusia turvallisuuskriittisiä kirjoitustoimintoja.")

    if "language_pack" in created_or_better_modules:
        if "build_language_context" not in _read_text_limited(root / "app" / "main.py"):
            next_steps.append("Kytke Finnish Language Pack LLM-vastauksen muodostukseen.")
    else:
        next_steps.append("Lisää Finnish Language Pack tai sen integraatio luonnollisemman suomen tueksi.")

    if "learning_feedback" in missing_modules:
        next_steps.append("Seuraava oppimisen kannalta tärkeä puuttuva osa on Learning Feedback Memory v1 Janin korjausten tallentamiseen.")

    if "memory_cleaner" in missing_modules:
        next_steps.append("Pidä memory_cleaner.py puuttuvana/suunniteltuna, kunnes se oikeasti luodaan, hyväksytään ja testataan.")

    tests = inspect_tests(root)
    ui = inspect_ui(root)
    audit = audit_status(root)
    recent_audit = read_audit_log(root, limit=5)

    return {
        "name": "Säde v1",
        "type": "local_ai_system",
        "report_type": "read_only_introspection",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(root),
        "state": "documented_and_developing",
        "documents": documents,
        "modules": modules,
        "verified_capabilities": [
            "read_only_project_status_report",
            "document_existence_check",
            "module_existence_check",
            "planned_vs_created_vs_implemented_separation",
            "automated_test_inventory",
            "ui_state_detection",
            "audit_chain_verification",
        ],
        "test_status": tests,
        "ui_status": ui,
        "audit_status": audit,
        "recent_audit_events": recent_audit.get("items", []),
        "recent_changes": recent_project_changes(root),
        "limitations": limitations,
        "next_steps": next_steps,
    }


def format_report_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# Säde v1 Introspection Report")
    lines.append("")
    lines.append(f"Luotu: {report['generated_at']}")
    lines.append(f"Projektijuuri: `{report['project_root']}`")
    lines.append("")
    lines.append("## 1. Mikä olen")
    lines.append("")
    lines.append(
        "Olen Säde v1, paikallinen AI-järjestelmä. Tämä raportti kuvaa "
        "dokumentoitua ja tiedostoista tarkistettua nykytilaani. "
        "Raportti ei väitä suunnitelmia toteutuksiksi."
    )
    lines.append("")
    lines.append("## 2. Dokumentit")
    lines.append("")
    lines.append("| id | tila | aktiivinen polku | huomio |")
    lines.append("|---|---|---|---|")
    for doc in report["documents"]:
        active_path = doc["active_path"] or "-"
        lines.append(f"| {doc['id']} | {doc['status']} | `{active_path}` | {doc['note']} |")

    lines.append("")
    lines.append("## 3. Moduulit")
    lines.append("")
    lines.append("| id | polku | tila | viittaukset | huomio |")
    lines.append("|---|---|---|---|---|")
    for module in report["modules"]:
        refs = ", ".join(module["referenced_by"]) if module["referenced_by"] else "-"
        lines.append(
            f"| {module['id']} | `{module['path']}` | {module['status']} | {refs} | {module['note']} |"
        )

    lines.append("")
    lines.append("## 4. Vahvistetut kyvyt")
    lines.append("")
    for capability in report["verified_capabilities"]:
        lines.append(f"- {capability}")

    lines.append("")
    lines.append("## 5. Testitila")
    lines.append("")
    tests = report["test_status"]
    lines.append(f"- Löydetyt testitiedostot: {len(tests['test_files'])}")
    lines.append(f"- Löydetyt testit: {tests['discovered_test_count']}")
    lines.append(f"- Viimeisin ajo: `{tests['last_run_status']}`")
    lines.append(f"- Huomio: {tests['note']}")

    lines.append("")
    lines.append("## 6. Käyttöliittymän nykytila")
    lines.append("")
    ui = report["ui_status"]
    lines.append(f"- Kieli: `{ui['language']}`")
    lines.append(f"- Chat ensin: `{ui['chat_first']}`")
    lines.append(f"- Välilehtityötila: `{ui['tabbed_workspace']}`")
    lines.append(f"- Välilehdet: {', '.join(ui['tabs']) or '-'}")
    lines.append(f"- Muisti ladataan pyynnöstä: `{ui['lazy_memory']}`")

    lines.append("")
    lines.append("## 7. Audit-lokin tila")
    lines.append("")
    audit = report["audit_status"]
    lines.append(f"- Eheä: `{audit.get('valid')}`")
    lines.append(f"- Tapahtumia: {audit.get('count', 0)}")
    lines.append(f"- Viimeisin tapahtuma: {audit.get('last_event_at') or '-'}")

    lines.append("")
    lines.append("## 8. Viimeksi muuttuneet projektitiedostot")
    lines.append("")
    for change in report["recent_changes"]:
        lines.append(f"- `{change['path']}` — {change['modified']} — `{change['sha256_12']}`")

    lines.append("")
    lines.append("## 9. Rajoitukset")
    lines.append("")
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")

    lines.append("")
    lines.append("## 10. Seuraavat askeleet")
    lines.append("")
    for step in report["next_steps"]:
        lines.append(f"- {step}")

    lines.append("")
    lines.append("## 11. Totuuslause")
    lines.append("")
    lines.append(
        "Suunnitelma ei ole toteutus. Luotu tiedosto ei ole vielä testattu ominaisuus. "
        "Tämä raportti erottaa nämä tilat toisistaan."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Säde v1 read-only introspection report")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Tulostusmuoto.",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Valinnainen projektijuuri. Oletus: introspection.py:n perusteella päätelty Sade-v1-juuri.",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve() if args.project_root else None
    report = build_introspection_report(root)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_report_markdown(report))


if __name__ == "__main__":
    main()
