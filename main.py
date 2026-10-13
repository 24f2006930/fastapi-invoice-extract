import os
import re
from datetime import date
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field, ValidationError
from fastapi.responses import JSONResponse

EMAIL = os.getenv("STUDENT_EMAIL", "24f2006930@ds.study.iitm.ac.in")

app = FastAPI(title="Invoice Field Extractor")


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1)


class InvoiceFields(BaseModel):
    vendor: str
    amount: float
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


@app.get("/")
async def root():
    return {"status": "ok", "endpoint": "/extract", "method": "POST"}


def extract_invoice(text: str) -> InvoiceFields:
    # Prefer explicit invoice labels, then use conservative fallbacks.
    vendor_patterns = [
        r"(?i)\b(?:vendor|supplier|seller|from|issued\s+by)\s*[:\-]\s*(.+?)(?=\s+(?:total\s+due|amount\s+due|grand\s+total|invoice\s+total|total|payment\s+due\s+date|due\s+date|pay\s+by)\b|[\r\n]|$)",
        r"(?i)\b([A-Z][A-Za-z0-9&.,'()\- ]{1,100}?\b(?:Industries|Industry|Ltd\.?|Limited|Inc\.?|LLC|Corp\.?|Corporation|Company|Co\.))\b",
    ]
    vendor = None
    for pattern in vendor_patterns:
        match = re.search(pattern, text)
        if match:
            vendor = match.group(1).strip().strip(" ,;")
            # Avoid accidentally treating a label or the whole invoice line as the vendor.
            if vendor:
                break

    currency = None
    currency_patterns = [
        r"(?i)\b(?:currency|currency\s+code)\s*[:=]\s*([A-Z]{3})\b",
        r"(?i)\b(USD|EUR|GBP)\b",
        r"(?<![A-Za-z])([$€£])\s*\d",
    ]
    for pattern in currency_patterns:
        match = re.search(pattern, text)
        if match:
            token = match.group(1).upper()
            currency = {"$": "USD", "€": "EUR", "£": "GBP"}.get(token, token)
            break

    # Look for explicit total-due labels before considering other numeric values.
    amount_patterns = [
        r"(?im)\b(?:total\s+amount\s+due|amount\s+due|total\s+due|balance\s+due|grand\s+total|invoice\s+total|total)\b\s*[:=\-]?\s*(?:USD|EUR|GBP|[$€£])?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
        r"(?i)\b(?:USD|EUR|GBP)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)\b",
        r"[$€£]\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
    ]
    amount = None
    for pattern in amount_patterns:
        matches = list(re.finditer(pattern, text))
        if matches:
            raw = matches[-1].group(1).replace(",", "")
            try:
                amount = float(raw)
                break
            except ValueError:
                pass

    # Due date labels first; then any ISO date in the text.
    date_patterns = [
        r"(?i)\b(?:payment\s+)?due\s+date\b\s*[:=\-]?\s*(\d{4}-\d{2}-\d{2})",
        r"(?i)\bpay\s+by\b\s*[:=\-]?\s*(\d{4}-\d{2}-\d{2})",
        r"\b(\d{4}-\d{2}-\d{2})\b",
    ]
    due_date = None
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1)
            try:
                date.fromisoformat(candidate)
                due_date = candidate
                break
            except ValueError:
                continue

    missing = []
    if not vendor:
        missing.append("vendor")
    if amount is None:
        missing.append("amount")
    if not currency:
        missing.append("currency")
    if not due_date:
        missing.append("date")
    if missing:
        raise ValueError("Could not extract required invoice fields: " + ", ".join(missing))

    return InvoiceFields(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=due_date,
    )


@app.post("/extract", response_model=InvoiceFields)
async def extract(body: ExtractRequest):
    text = body.text.strip()
    if not text:
        return JSONResponse(status_code=422, content={"detail": "text must not be empty"})
    try:
        fields = extract_invoice(text)
        return fields
    except (ValueError, ValidationError):
        # Best-effort malformed/garbage handling: a validation response, never HTTP 500.
        return JSONResponse(status_code=422, content={"detail": "Could not extract valid invoice fields"})
