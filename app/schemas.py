from pydantic import BaseModel, Field
from typing import Any, Literal, Optional

DocType = Literal["quote", "invoice"]

class ProposalGenerateIn(BaseModel):
    user_id: str
    client_id: Optional[str] = None
    proposal_ref: str
    input_raw: str
    options: dict[str, Any] = Field(default_factory=dict)

class ProposalGenerateOut(BaseModel):
    structured_context: dict[str, Any]
    output_full: str
    output_exec: str
    output_email: str
    output_dm: str
    warnings: list[str] = Field(default_factory=list)

class BuildDocumentIn(BaseModel):
    user_id: str
    proposal_id: str
    doc_type: DocType
    overrides: dict[str, Any] = Field(default_factory=dict)

    identity_profile: Optional[dict[str, Any]] = None
    visual_financial_profile: Optional[dict[str, Any]] = None
    client_profile: Optional[dict[str, Any]] = None
    proposal: Optional[dict[str, Any]] = None

class LineItem(BaseModel):
    no: int
    description: str
    unit_price: float
    qty: float
    total: float

class RenderPayload(BaseModel):
    doc_type: DocType
    doc_number: str
    issue_date: str
    due_date: Optional[str] = None
    valid_until: Optional[str] = None
    proposal_ref: str

    company: dict[str, Any]
    client: dict[str, Any]

    line_items: list[LineItem]
    subtotal: float
    tax: float
    total: float
    notes: Optional[str] = None

class RenderOut(BaseModel):
    pdf_bytes_base64: str
    png4k_bytes_base64: str
