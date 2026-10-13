# FastAPI Invoice Field Extractor

A FastAPI service that extracts structured invoice fields from free-form text and validates the response using Pydantic. Deployed on Render.

**Live endpoint:** https://fastapi-invoice-extract.onrender.com/extract

## Endpoint

### `POST /extract`

Accepts invoice text in a JSON request body.

**Request example:**

```json
{
  "text": "Vendor: Acme-1234 Industries Ltd.\nTotal Due: USD 1250.50\nPayment Due Date: 2026-08-21"
}
```

**Response example:**

```json
{
  "vendor": "Acme-1234 Industries Ltd.",
  "amount": 1250.5,
  "currency": "USD",
  "date": "2026-08-21"
}
```

## Extracted Fields

- **`vendor`** — vendor name extracted from the invoice text.
- **`amount`** — total amount due as a number.
- **`currency`** — uppercase, three-letter currency code, such as `USD`, `EUR`, or `GBP`.
- **`date`** — payment due date in `YYYY-MM-DD` format.

The service processes each submitted invoice dynamically rather than returning hard-coded sample values.

## Validation and Error Handling

The response uses a Pydantic model to validate the output structure and field formats.

- Valid invoice text returns HTTP `200 OK`.
- Empty input returns HTTP `422 Unprocessable Entity`.
- Unparseable invoice text returns HTTP `422` rather than HTTP `500`.

## Implementation

The current implementation uses deterministic text extraction with regular expressions and Pydantic validation. It does **not** invoke a local LLM runtime.

## Deployment

The service is deployed on Render using a Blueprint configuration in `render.yaml`.

## Quick Test

Run the following command in a terminal:

```bash
curl -i -X POST "https://fastapi-invoice-extract.onrender.com/extract" \
  -H "Content-Type: application/json" \
  -d '{"text":"Vendor: Acme-1234 Industries Ltd. Total Due: USD 1250.50 Payment Due Date: 2026-08-21"}'
```

Expected output:

```json
{
  "vendor": "Acme-1234 Industries Ltd.",
  "amount": 1250.5,
  "currency": "USD",
  "date": "2026-08-21"
}
```

## Project Structure

```text
fastapi-invoice-extract/
├── main.py
├── requirements.txt
├── render.yaml
└── README.md
```
