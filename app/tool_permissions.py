from __future__ import annotations

"""Työkalujen riskitasot ja käyttöoikeuspolitiikka Säde v1:lle."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


RISK_ORDER = {
    "read": 1,
    "search": 2,
    "medium": 3,
    "memory_write": 4,
    "file_write": 5,
    "high": 5,
    "system": 6,
    "critical": 7,
}


@dataclass(frozen=True)
class ToolPolicy:
    name: str
    risk_level: str
    writes: bool
    requires_audit: bool
    requires_confirmation: bool
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "risk_level": self.risk_level,
            "writes": self.writes,
            "requires_audit": self.requires_audit,
            "requires_confirmation": self.requires_confirmation,
            "description": self.description,
        }


POLICIES: Dict[str, ToolPolicy] = {
    "list_tools": ToolPolicy("list_tools", "read", False, False, False, "Listaa käytettävissä olevat työkalut."),
    "tools_status": ToolPolicy("tools_status", "read", False, False, False, "Näyttää työkalukerroksen tilan."),
    "project_status": ToolPolicy("project_status", "read", False, False, False, "Näyttää projektin perustilan."),
    "list_files": ToolPolicy("list_files", "read", False, False, False, "Listaa projektikansion tiedostoja."),
    "read_file": ToolPolicy("read_file", "read", False, True, False, "Lukee sallitun tekstitiedoston projektin sisältä."),
    "semantic_search": ToolPolicy("semantic_search", "search", False, False, False, "Hakee semanttisesta muistista."),
    "rag_search": ToolPolicy("rag_search", "search", False, False, False, "Hakee RAG-kontekstia."),
    "web_search": ToolPolicy("web_search", "search", False, True, False, "Tekee eksplisiittisen verkkohakupyynnön."),
    "web_source_review": ToolPolicy("web_source_review", "read", False, False, False, "Tarkistaa viimeisimmän verkkohakutuloksen lähteet."),
    "write_file": ToolPolicy("write_file", "file_write", True, True, True, "Kirjoittaa tiedoston projektikansioon."),
    "append_file": ToolPolicy("append_file", "file_write", True, True, True, "Lisää tekstiä tiedostoon projektikansiossa."),
    "write_or_append_file": ToolPolicy("write_or_append_file", "file_write", True, True, True, "Kirjoittaa tai lisää tiedostoon."),
    "ingest_file": ToolPolicy("ingest_file", "memory_write", True, True, False, "Lisää tiedoston sisällön muisti- ja RAG-kontekstiin."),
    "memory_save": ToolPolicy("memory_save", "memory_write", True, True, False, "Tallentaa käyttäjän eksplisiittisen muiston."),
    "learning_feedback": ToolPolicy("learning_feedback", "memory_write", True, True, False, "Tallentaa käyttäjän oppimispalautteen."),
    "memory_cleanup_preview": ToolPolicy("memory_cleanup_preview", "read", False, False, False, "Esikatselee muistihuollon poistoehdokkaita."),
    "memory_cleanup_apply": ToolPolicy("memory_cleanup_apply", "critical", True, True, True, "Poistaa hyväksyttyjä muistimerkintöjä."),
    "rebuild_semantic_index": ToolPolicy("rebuild_semantic_index", "high", True, True, True, "Rakentaa semanttisen indeksin uudelleen."),
    "update_system_prompt": ToolPolicy("update_system_prompt", "critical", True, True, True, "Muokkaa Säteen ydinpromptia."),
    "backup": ToolPolicy("backup", "medium", True, True, False, "Luo varmuuskopion."),
    "restore": ToolPolicy("restore", "critical", True, True, True, "Palauttaa tiedostoja varmuuskopiosta."),
    "debug_trace": ToolPolicy("debug_trace", "read", False, True, False, "Näyttää kehittäjän jäljitystietoja."),
}


def get_tool_policy(tool_name: str) -> Dict[str, Any]:
    policy = POLICIES.get(tool_name)
    if policy:
        return policy.to_dict()
    return ToolPolicy(
        name=tool_name,
        risk_level="medium",
        writes=False,
        requires_audit=True,
        requires_confirmation=False,
        description="Tuntematon tai erikseen rekisteröimätön työkalu.",
    ).to_dict()


def list_tool_policies() -> Dict[str, Any]:
    policies = [policy.to_dict() for policy in sorted(POLICIES.values(), key=lambda item: item.name)]
    return {
        "ok": True,
        "version": "tool-permissions-v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "risk_order": RISK_ORDER,
        "policies": policies,
    }


def annotate_tool_result(tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    annotated = dict(result or {})
    annotated["tool_policy"] = get_tool_policy(tool_name)
    return annotated


def risk_at_least(risk_level: str, threshold: str) -> bool:
    return RISK_ORDER.get(risk_level, 3) >= RISK_ORDER.get(threshold, 3)


def validate_tool_execution(tool_name: str, *, confirmed: bool = False) -> Dict[str, Any]:
    policy = get_tool_policy(tool_name)
    if policy["requires_confirmation"] and not confirmed:
        return {
            "ok": False,
            "allowed": False,
            "tool": tool_name,
            "policy": policy,
            "message": "Työkalu vaatii erillisen käyttäjän hyväksynnän ennen suoritusta.",
        }
    return {
        "ok": True,
        "allowed": True,
        "tool": tool_name,
        "policy": policy,
    }

