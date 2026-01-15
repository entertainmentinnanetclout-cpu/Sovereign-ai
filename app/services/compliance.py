WEAK_PHRASES = [
    "just checking", "hope you", "if possible", "sorry", "i was wondering",
    "please let me know if you can", "no worries"
]

def enforce_no_weak_language(text: str) -> str:
    t = text
    for p in WEAK_PHRASES:
        t = t.replace(p, "")
        t = t.replace(p.title(), "")
    return t

def require_cta(text: str) -> None:
    must = ["next step", "let's", "lets", "schedule", "confirm", "approve"]
    low = text.lower()
    if not any(m in low for m in must):
        raise ValueError("Missing CTA (call-to-action)")

def validate_totals(line_items: list[dict], subtotal: float, tax: float, total: float) -> None:
    calc = round(sum(float(i["total"]) for i in line_items), 2)
    if round(subtotal, 2) != calc:
        raise ValueError(f"Subtotal mismatch: expected {calc}, got {subtotal}")
    if round(subtotal + tax, 2) != round(total, 2):
        raise ValueError("Total mismatch: subtotal + tax != total")
