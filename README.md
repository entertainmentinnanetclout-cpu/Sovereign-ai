# Sovereign AI Core

This repository contains the Sovereign AI Core service used by the Lovable app
to generate proposals, quotations, and invoices without relying on Lovable AI
or external LLM providers.

## What This Service Does
- Proposal generation (rules-based)
- Quote and invoice generation
- Locked PDF + 4K PNG rendering
- Deterministic compliance and totals validation

## Tech Stack
- Python 3.11
- FastAPI
- ReportLab (PDF)
- Render (hosting)

## Environment Variables
- SOVEREIGN_INTERNAL_KEY
- TZ

## Health Check
GET /health
