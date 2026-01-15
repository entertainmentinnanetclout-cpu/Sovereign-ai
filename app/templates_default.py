TEMPLATES = {
  "proposal_full": {
    "sections": [
      {"title": "{{company_name}} — Strategic Proposal", "body": "Proposal Reference: {{proposal_ref}}\nPrepared for: {{client_name}}\n"},
      {"title": "Strategic Context", "body": "This proposal outlines a clear, execution-ready approach to deliver outcomes aligned with your priorities."},
      {"title": "Opportunity Framing", "body": "The opportunity is to implement a focused solution that improves speed, reliability, and measurable outcomes—without unnecessary complexity."},
      {"title": "Proposed Solution", "body": "We will deliver a structured implementation with clear milestones, defined deliverables, and controlled risk."},
      {"title": "Value to You", "body": "You receive a direct uplift through reduced friction, improved turnaround, and a process that scales."},
      {"title": "Mutual Alignment", "body": "This engagement is commercially fair and operationally clean—clear scope, clear outcomes, clear responsibilities."},
      {"title": "Risk Reduction", "body": "Risk is managed through phased delivery, milestone sign-offs, and tight scope control. Changes are handled via written variation."},
      {"title": "Next Steps", "body": "Next step: confirm acceptance of the scope and timeline, and we will issue the quotation/invoice and schedule kickoff."}
    ]
  },
  "proposal_exec": {
    "sections": [
      {"title": "Executive Summary", "body": "{{company_name}} proposes a structured delivery plan aligned to your priorities. Proposal Ref: {{proposal_ref}}"},
      {"title": "Next Steps", "body": "Confirm acceptance of scope and commercial terms, then kickoff scheduling follows immediately."}
    ]
  },
  "proposal_email": {
    "sections": [
      {"title": "Subject: Proposal — {{company_name}} ({{proposal_ref}})",
       "body": "Hello {{client_name}},\n\nAttached is the proposal outlining the approach, deliverables, and next steps.\n\nIf aligned, confirm acceptance so we can issue the quotation/invoice and schedule kickoff.\n\nRegards,\n{{company_name}}"}
    ]
  },
  "proposal_dm": {
    "sections": [
      {"title": "", "body": "Hi {{client_name}} — Proposal ready ({{proposal_ref}}). Next step is confirmation so I can issue the quotation/invoice and schedule kickoff."}
    ]
  }
}
