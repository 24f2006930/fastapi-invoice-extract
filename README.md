# FastAPI Invoice Field Extractor

A FastAPI service that extracts vendor, amount, currency, and due date from free-form invoice text and validates the response using a Pydantic model.

## Repository name

`fastapi-invoice-extract`

## Repository description

FastAPI invoice extraction API with Pydantic-validated vendor, amount, currency, and due-date fields, plus safe validation errors for malformed input.

## Endpoint

`POST /extract`

Request:

```json
{
  "text": "Vendor: Acme-1234 Industries Ltd.\nTotal Due: USD 1250.50\nPayment Due Date: 2026-08-21"
}
```

Example response:

```json
{
  "vendor": "Acme-1234 Industries Ltd.",
  "amount": 1250.5,
  "currency": "USD",
  "date": "2026-08-21"
}
```

The service extracts values from each submitted text rather than returning hard-coded invoice data. The response model validates the currency code and ISO date format. Empty or unparseable input returns HTTP 422 rather than HTTP 500.

## Implementation note

This deployable starter uses deterministic text extraction and Pydantic validation. It does not call an LLM runtime. If the assignment environment specifically requires inference through a local LLM, deploy the model runtime separately (for example, Ollama) and connect the API to it; a hosted web service cannot access a model running only on your personal computer unless you expose that runtime securely.

## Deploy on Render

Create a Blueprint from this repository using `render.yaml`. Verify `STUDENT_EMAIL` matches the email shown by the assignment.

## Quick test

```bash
curl -i -X POST "https://YOUR-SERVICE.onrender.com/extract" \
  -H "Content-Type: application/json" \
  -d '{"text":"Vendor: Acme-1234 Industries Ltd. Total Due: USD 1250.50 Payment Due Date: 2026-08-21"}'
```
