from __future__ import annotations

"""RAG-haun laadun mittaus ja lähderajan tarkistus."""

from typing import Any, Dict, List


def evaluate_rag_quality(search_result: Dict[str, Any], *, query: str = "") -> Dict[str, Any]:
    results: List[Dict[str, Any]] = list(search_result.get("results") or [])
    count = len(results)
    scores = [float(item.get("score", 0.0) or 0.0) for item in results]
    coverages = [float(item.get("term_coverage", 0.0) or 0.0) for item in results]
    source_paths = [item.get("path") or item.get("source") for item in results if item.get("path") or item.get("source")]
    unique_sources = sorted({str(source) for source in source_paths if source})
    has_text = all(str(item.get("text", "")).strip() for item in results) if results else False
    has_reasons = all(item.get("reasons") for item in results) if results else False
    enough_sources = count >= 1 and len(unique_sources) >= 1
    min_score = min(scores) if scores else 0.0
    avg_coverage = sum(coverages) / len(coverages) if coverages else 0.0
    citation_ready = enough_sources and has_text and has_reasons

    warnings: List[str] = []
    if not count:
        warnings.append("no_results")
    if count and min_score < float(search_result.get("min_score", 0.0) or 0.0):
        warnings.append("below_declared_min_score")
    if count and avg_coverage < 0.5:
        warnings.append("low_term_coverage")
    if count and not has_reasons:
        warnings.append("missing_ranking_reasons")

    return {
        "ok": True,
        "version": "rag-quality-v1",
        "query": query or search_result.get("query", ""),
        "result_count": count,
        "unique_source_count": len(unique_sources),
        "unique_sources": unique_sources,
        "min_score": round(min_score, 3),
        "average_term_coverage": round(avg_coverage, 3),
        "citation_ready": citation_ready,
        "uncertainty_required": not citation_ready,
        "warnings": warnings,
        "quality_gate_passed": citation_ready and not warnings,
    }


def format_rag_quality_reply(quality: Dict[str, Any]) -> str:
    if quality.get("quality_gate_passed"):
        return (
            "RAG-laatu hyväksytty: lähde löytyy, tekstikatkelmat ovat mukana ja valintaperusteet näkyvät. "
            f"Lähteitä: {quality.get('unique_source_count')}, keskimääräinen kattavuus: {quality.get('average_term_coverage')}."
        )
    return (
        "RAG-laatu ei vielä läpäise porttia. "
        f"Varoitukset: {', '.join(quality.get('warnings') or ['tuntematon'])}. "
        "Tällöin Säteen pitää kertoa epävarmuus eikä keksiä vastausta."
    )

