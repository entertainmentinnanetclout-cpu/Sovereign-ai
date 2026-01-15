import re
from typing import Any

DEAL_KEYWORDS = {
    "retainer": ["monthly", "per month", "ongoing", "maintenance", "retainer"],
    "procurement": ["tender", "procurement", "rfp", "compliance"],
    "funding": ["investment", "equity", "seed", "funding", "investor"],
    "partnership": ["partner", "partnership", "collab", "revenue share", "joint"],
    "service": ["build", "develop", "deliver", "scope", "service", "project"],
}

def _score_deal_type(text: str) -> dict[str, int]:
    t = text.lower()
    scores = {k: 0 for k in DEAL_KEYWORDS.keys()}
    for deal, kws in DEAL_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[deal] += 2
    return scores

def parse_intent(input_raw: str) -> dict[str, Any]:
    raw = (input_raw or "").strip()
    scores = _score_deal_type(raw)
    deal_type = max(scores, key=scores.get) if max(scores.values()) > 0 else "other"

    money_hint = re.findall(r"(?:R|ZAR)\s?\d[\d,]*(?:\.\d{1,2})?", raw)
    timeline_hint = " ".join(re.findall(r"(?:\b\d+\s?(?:days|weeks|months)\b)", raw.lower()))

    risk_flags = []
    if not money_hint:
        risk_flags.append("pricing_missing")
    if len(raw) < 20:
        risk_flags.append("deliverables_unclear")
    if not timeline_hint:
        risk_flags.append("timeline_missing")

    return {
        "recipient": {"name": "", "entity": "", "type": "sme", "role": ""},
        "deal": {
            "deal_type": deal_type,
            "topic": "",
            "offer": "",
            "recipient_benefit": "",
            "user_benefit": "",
            "timeline": timeline_hint,
            "pricing_model": "unknown",
            "budget_hint": money_hint[0] if money_hint else "",
        },
        "signals": {
            "urgency": "medium",
            "assertiveness": "balanced",
            "risk_flags": risk_flags,
        },
        "raw": raw,
    }
