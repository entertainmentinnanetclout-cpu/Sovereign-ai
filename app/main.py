from fastapi import FastAPI, Depends, HTTPException
from .security import require_internal_key
from .schemas import ProposalGenerateIn, ProposalGenerateOut, BuildDocumentIn, RenderPayload, RenderOut
from .templates_default import TEMPLATES
from .services.deal_os import generate_proposal
from .services.compliance import validate_totals
from .services.render import render_invoice_quote, b64

app = FastAPI(title="Sovereign AI", version="1.0.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"ok": True, "service": "Sovereign AI Core", "health": "/health"}

@app.post("/v1/proposals/generate", response_model=ProposalGenerateOut, dependencies=[Depends(require_internal_key)])
def proposals_generate(payload: ProposalGenerateIn):
    # In production: pass identity/client from Supabase via Edge
    identity = {
        "company_name": payload.options.get("company_name", "YOUR COMPANY"),
        "industry": payload.options.get("industry", ""),
        "value_proposition": payload.options.get("value_proposition", ""),
    }
    client = {"client_name": payload.options.get("client_name", ""), "client_entity": ""}

    result = generate_proposal(
        identity=identity,
        client=client,
        proposal_ref=payload.proposal_ref,
        input_raw=payload.input_raw,
        templates=TEMPLATES,
        options=payload.options,
    )
    return ProposalGenerateOut(**result)

@app.post("/v1/commerce/build-document", dependencies=[Depends(require_internal_key)])
def build_document(payload: BuildDocumentIn):
    proposal = payload.proposal or {}
    client = payload.client_profile or {}
    vf = payload.visual_financial_profile or {}
    identity = payload.identity_profile or {}

    company = {
        "company_name": (identity.get("company_name") or "YOUR COMPANY").strip(),
        "tagline": identity.get("tagline", ""),
        "billing_address": vf.get("billing_address", ""),
        "reg_number": vf.get("reg_number", ""),
        "vat_number": vf.get("vat_number", ""),
        "brand_accent_color": vf.get("brand_accent_color", "#0A66C2"),
        "payment_terms_default": vf.get("payment_terms_default", "NET 7"),
        "bank_details": vf.get("bank_details", {}) or {},
        "email": identity.get("email", ""),
        "website": identity.get("website", ""),
        "signatory_name": identity.get("signatory_name", ""),
        "signatory_role": identity.get("signatory_role", "Director"),
    }

    prefix = "INV" if payload.doc_type == "invoice" else "QUO"
    suffix = (proposal.get("proposal_ref") or "00000").replace("SOP-", "").replace("/", "-")
    doc_number = f"{prefix}-{suffix}"

    import datetime as dt
    today = dt.date.today()
    issue_date = str(today)
    due_date = str(today + dt.timedelta(days=7)) if payload.doc_type == "invoice" else None
    valid_until = str(today + dt.timedelta(days=7)) if payload.doc_type == "quote" else None

    items_in = (payload.overrides or {}).get("line_items") or [{"description": "SERVICES AS PER PROPOSAL", "unit_price": 0.0, "qty": 1}]
    line_items = []
    for i, it in enumerate(items_in, start=1):
        unit = float(it.get("unit_price", 0.0))
        qty = float(it.get("qty", 1))
        total = round(unit * qty, 2)
        line_items.append({"no": i, "description": it.get("description", ""), "unit_price": unit, "qty": qty, "total": total})

    subtotal = round(sum(i["total"] for i in line_items), 2)
    tax_rate = float((payload.overrides or {}).get("tax_rate", 0.0))
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    validate_totals(line_items, subtotal, tax, total)

    proposal_ref = proposal.get("proposal_ref") or ""
    if not proposal_ref:
        raise HTTPException(status_code=400, detail="Proposal reference missing. Proposal linking is mandatory.")

    return {
        "doc_type": payload.doc_type,
        "doc_number": doc_number,
        "issue_date": issue_date,
        "due_date": due_date,
        "valid_until": valid_until,
        "proposal_ref": proposal_ref,
        "company": company,
        "client": {
            "client_name": client.get("client_name", ""),
            "client_entity": client.get("client_entity", ""),
            "client_email": client.get("client_email", ""),
            "client_address": client.get("client_address", ""),
        },
        "line_items": line_items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "notes": (payload.overrides or {}).get("notes"),
    }

@app.post("/v1/render/invoice-quote", response_model=RenderOut, dependencies=[Depends(require_internal_key)])
def render_endpoint(payload: RenderPayload):
    pdf_bytes, png_bytes = render_invoice_quote(payload.model_dump())
    return RenderOut(pdf_bytes_base64=b64(pdf_bytes), png4k_bytes_base64=b64(png_bytes))
