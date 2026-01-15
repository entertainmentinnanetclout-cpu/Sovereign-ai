from typing import Any
from .intent import parse_intent
from .compliance import enforce_no_weak_language, require_cta

def _render_sections(sections: list[dict[str, Any]], ctx: dict[str, Any]) -> str:
    out = []
    for sec in sections:
        title = (sec.get("title") or "").strip()
        body = (sec.get("body") or "").strip()

        for k, v in ctx.items():
            if isinstance(v, (str, int, float)):
                body = body.replace("{{" + k + "}}", str(v))
                title = title.replace("{{" + k + "}}", str(v))

        if title:
            out.append(title)
        if body:
            out.append(body)
        out.append("")
    return "\n".join(out).strip()

def generate_proposal(identity: dict[str, Any], client: dict[str, Any], proposal_ref: str, input_raw: str, templates: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    structured = parse_intent(input_raw)
    structured["proposal_ref"] = proposal_ref
    structured["signals"]["assertiveness"] = (options or {}).get("assertiveness", "balanced")

    ctx = {
        "company_name": identity.get("company_name", ""),
        "client_name": client.get("client_name", ""),
        "proposal_ref": proposal_ref,
    }

    full = _render_sections(templates["proposal_full"]["sections"], ctx)
    execv = _render_sections(templates["proposal_exec"]["sections"], ctx)
    email = _render_sections(templates["proposal_email"]["sections"], ctx)
    dm = _render_sections(templates["proposal_dm"]["sections"], ctx)

    full = enforce_no_weak_language(full)
    email = enforce_no_weak_language(email)

    require_cta(full)
    require_cta(email)

    return {
        "structured_context": structured,
        "output_full": full,
        "output_exec": execv,
        "output_email": email,
        "output_dm": dm,
        "warnings": structured["signals"]["risk_flags"],
    }
