
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import re

VERSION = "1.0"


def _norm(text: str) -> str:
    text = str(text or "").strip().lower()
    text = text.replace("ä", "a").replace("ö", "o")
    return re.sub(r"\s+", " ", text)


def _hits(text: str, words: list[str]) -> list[str]:
    return [word for word in words if word in text]


def behavior_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "message": "Behavior Layer v1 on käytettävissä.",
        "version": VERSION,
        "mode": "lightweight_rule_based",
        "uses_heavy_model": False,
        "local_gpu_required": False,
        "purpose": [
            "tunnistaa viestin intentio",
            "arvioida viestin sävyä ilman diagnooseja",
            "ehdottaa vastaustyyliä",
            "auttaa Sädettä valitsemaan tilanteeseen sopivan tavan vastata",
        ],
        "limitations": [
            "ei tee diagnooseja",
            "ei päättele pysyviä persoonallisuuspiirteitä",
            "ei korvaa Human Behavior Atlas / OmniSapiens -mallia",
        ],
    }


def analyze_behavior(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    normalized = _norm(text)

    signals = {
        "technical_debugging": _hits(normalized, [
            "virhe", "error", "traceback", "syntaxerror", "exception", "ei toimi",
            "kaatuu", "bugi", "500", "422", "powershell", "python", "uvicorn",
            "endpoint", "internal server error", "korjaa", "patch",
        ]),
        "frustration": _hits(normalized, [
            "kovapainen", "kovapäinen", "taas", "vielakin", "vieläkin",
            "ei onnistu", "arsyttaa", "ärsyttää", "perkele", "helvetti",
        ]),
        "positive": _hits(normalized, [
            "jee", "jes", "hyva", "hyvä", "onnistui", "toimii", ":d",
            "kiitos", "mahtavaa", "hienoa",
        ]),
        "build": _hits(normalized, [
            "tehdaan", "tehdään", "rakennetaan", "jatketaan", "lisataan",
            "lisätään", "asennetaan", "tee", "teemme",
        ]),
        "uncertain": _hits(normalized, [
            "miksi", "miten", "onkohan", "ehka", "ehkä", "taitaa",
            "en ymmarra", "en ymmärrä", "voiko",
        ]),
        "support": _hits(normalized, [
            "raskas", "ahdistaa", "pelottaa", "huolestuttaa", "vasynyt",
            "väsynyt", "stressaa", "en jaksa",
        ]),
        "decision": _hits(normalized, [
            "kannattaako", "riittaako", "riittääkö", "suositus", "vertailu",
            "mika parempi", "mikä parempi",
        ]),
        "humor": _hits(normalized, [
            ":d", "haha", "hehe", "pölja", "pöljä",
            "kovapainen yksilo", "kovapäinen yksilö",
        ]),
    }

    active = {key: value for key, value in signals.items() if value}

    if signals["technical_debugging"]:
        intent = "technical_debugging"
    elif signals["build"]:
        intent = "build_or_modify_system"
    elif signals["decision"]:
        intent = "decision_support"
    elif signals["support"]:
        intent = "emotional_support"
    elif signals["uncertain"]:
        intent = "explanation_needed"
    else:
        intent = "general_conversation"

    if signals["positive"] and signals["frustration"]:
        tone = "leikkisä mutta hieman turhautunut"
    elif signals["positive"]:
        tone = "innostunut / tyytyväinen"
    elif signals["frustration"]:
        tone = "turhautunut"
    elif signals["support"]:
        tone = "kuormittunut tai huolestunut"
    elif signals["uncertain"]:
        tone = "epävarma / selvyyttä hakeva"
    elif signals["humor"]:
        tone = "leikkisä"
    else:
        tone = "neutraali"

    styles = {
        "technical_debugging": "lämmin, lyhyt, komento ensin, selitys sen jälkeen",
        "build_or_modify_system": "käytännöllinen, vaiheittainen, backup ensin",
        "decision_support": "suora, vertaileva, riskit näkyviin",
        "emotional_support": "lempeä, rauhallinen, validoiva",
        "explanation_needed": "selkeä, konkreettinen, ei teoriaähkyä",
        "general_conversation": "selkeä, lämmin ja käytännöllinen",
    }

    risky = _hits(normalized, [
        "poista kaikki", "delete all", ".env", "salasana", "password",
        "api key", "token", "pankki", "maksu",
    ])

    if risky:
        risk = "high"
    elif intent == "emotional_support":
        risk = "sensitive"
    elif intent in {"technical_debugging", "build_or_modify_system"}:
        risk = "medium"
    else:
        risk = "low"

    return {
        "ok": True,
        "version": VERSION,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "intent": intent,
        "tone": tone,
        "risk_level": risk,
        "response_style": styles[intent],
        "signals": active,
        "recommended_assistant_behavior": {
            "be_warm": True,
            "be_direct": intent in {"technical_debugging", "build_or_modify_system", "decision_support"},
            "give_commands_first": intent == "technical_debugging",
            "avoid_overexplaining": intent in {"technical_debugging", "build_or_modify_system"},
            "use_extra_care": risk in {"high", "sensitive"},
        },
        "guardrail": "Tämä ei ole diagnoosi, vain viestin sävyn ja tarpeen kevyt tulkinta.",
        "input_length": len(str(text or "")),
    }


def format_behavior_summary(result: Dict[str, Any]) -> str:
    lines = [
        "Behavior Layer v1 -analyysi:",
        "",
        f"Intentio: {result.get('intent')}",
        f"Sävy: {result.get('tone')}",
        f"Riskitaso: {result.get('risk_level')}",
        f"Vastaustyyli: {result.get('response_style')}",
    ]

    signals = result.get("signals") or {}

    if signals:
        lines.append("")
        lines.append("Havaitut signaalit:")

        for key, values in signals.items():
            lines.append(f"- {key}: {', '.join(values[:8])}")

    return "\n".join(lines).strip()
