# Product Requirements Document (PRD) — Invoice Parsing API & UI Prototype

## 0) Meta

* **PRD ID:** PRD-20251020-INVOICE-PARSER
* **Version:** 1.0
* **Status:** Draft
* **Last Updated:** 2025-10-20
* **Owners:** James Simmons (PM/Eng) — [james.simmons@fortiumpartners.com](mailto:james.simmons@fortiumpartners.com)
* **Contributors/Reviewers:** TBD (Design, Engineering, QA)
* **Related Artifacts:** TRD (to be created), UI prototype on Vercel

---

## 1) Purpose & Context

* **Problem Statement:** Businesses receive invoices in diverse formats—PDFs, images, emails, and text—with no consistent structure, creating bottlenecks in financial data ingestion.
* **Goal/Outcome:** Build an AI-powered API that parses invoices of any format into structured, machine-readable data suitable for ERP and finance system ingestion.
* **Personas/Targets:** Finance ops engineers, accountants, ERP integrators.
* **Assumptions:** GPT-4o has robust OCR and semantic understanding capabilities.
* **Constraints:** Stateless v1; limited to invoices ≤ 5MB; response time ≤ 10s per document.
* **Non-Goals:** Vendor-specific template handling, data persistence, or user authentication in v1.

---

## 2) Scope Overview

* **Core Use Cases:**

  1. User uploads invoice file (PDF, image, or text).
  2. Backend uses GPT-4o to extract structured data via a unified schema.
  3. Frontend displays parsed output in JSON.
  4. Downstream systems consume via API (future).
* **User Journeys:** Upload → Parse → Review output → Copy or export data.
* **Key Risks & Unknowns:** OCR edge cases, multilingual invoices, low-quality scans.

---

## 3) Functional Requirements

### 3.1 Index

| Req ID  | Title                     | Priority | Status      | Depends On | Conflicts With |
| ------- | ------------------------- | -------- | ----------- | ---------- | -------------- |
| REQ-001 | Invoice Upload Endpoint   | Must     | Not Started |            |                |
| REQ-002 | GPT-4o Semantic Parser    | Must     | Not Started | REQ-001    |                |
| REQ-003 | Output Schema Enforcement | Must     | Not Started | REQ-002    |                |
| REQ-004 | React UI Prototype        | Should   | Not Started | REQ-001    |                |
| REQ-005 | Vercel Deployment         | Should   | Not Started | REQ-004    |                |

### 3.2 Details

#### REQ-001 — Invoice Upload Endpoint

* **Description:** Provide a POST endpoint to accept files (PDF/image/text).
* **Actors:** User, System.
* **Preconditions:** Valid file; ≤5MB.
* **Main Flow:** Receive file → Validate → Pass to GPT-4o parser.
* **Telemetry:** upload.count, upload.size.avg
* **Success Metrics:** ≥95% successful uploads.
* **Priority:** Must

**Acceptance Criteria (Gherkin)**

```gherkin
Scenario: Upload valid invoice
  Given a PDF invoice file under 5MB
  When the file is uploaded via POST /api/parse
  Then the system accepts it and responds 202 Accepted
```

#### REQ-002 — GPT-4o Semantic Parser

* **Description:** Use GPT-4o to extract fields from arbitrary invoices (text, PDF, or image).
* **Actors:** Backend System, GPT-4o API.
* **Success Metrics:** ≥90% field accuracy vs ground truth (manual validation).
* **Priority:** Must

**Acceptance Criteria (Gherkin)**

```gherkin
Scenario: Parse invoice with unknown layout
  Given an invoice of arbitrary vendor format
  When processed by GPT-4o
  Then the system returns structured JSON following the invoice schema
```

#### REQ-003 — Output Schema Enforcement

* **Description:** Validate and normalize GPT output against canonical schema.
* **Schema:** Supplier, Customer, Invoice summary, Line items, Metadata.
* **Priority:** Must

#### REQ-004 — React UI Prototype

* **Description:** Stateless UI with upload box and structured data viewer.
* **Priority:** Should
* **Status:** Not Started

#### REQ-005 — Vercel Deployment

* **Description:** Deploy backend (FastAPI) and frontend (React) to Vercel/Railway.
* **Priority:** Should

---

## 4) Non-Functional Requirements

| NFR ID  | Category    | Statement (Measurable)      | Metric/Method    | Priority | Status      |
| ------- | ----------- | --------------------------- | ---------------- | -------- | ----------- |
| NFR-001 | Performance | Parse ≤10s for files ≤5MB   | Integration test | Must     | Not Started |
| NFR-002 | Reliability | 99% uptime (API health)     | Monitoring       | Should   | Not Started |
| NFR-003 | Security    | Validate input MIME & size  | Static test      | Must     | Not Started |
| NFR-004 | Privacy     | Do not persist invoice data | Code review      | Must     | Not Started |

---

## 5) Data & Interfaces

### Invoice Schema v1.1

```json
{
  "supplier": { "name": "string", "address": "string", "phone": "string", "email": "string", "tax_id": "string" },
  "customer": { "name": "string", "address": "string", "account_id": "string" },
  "invoice": { "number": "string", "issue_date": "YYYY-MM-DD", "due_date": "YYYY-MM-DD", "currency": "string", "subtotal": "number", "tax": "number", "total": "number", "payment_terms": "string", "po_number": "string" },
  "line_items": [ { "sku": "string", "description": "string", "quantity": "number", "unit_price": "number", "discount": "number", "tax_rate": "number", "total": "number" } ],
  "meta": { "source_file_name": "string", "source_format": "pdf|image|text", "confidence_score": "number", "model_version": "string", "extraction_time": "ISO 8601" }
}
```

---

## 6) Implementation Plan & Status

| Work Item   | Coverage (Req/NFR IDs) | Priority | Status      | Owner | ETA |
| ----------- | ---------------------- | -------- | ----------- | ----- | --- |
| Backend API | REQ-001–REQ-003        | Must     | Not Started |       |     |
| Frontend UI | REQ-004                | Should   | Not Started |       |     |
| Deployment  | REQ-005, NFR-001       | Should   | Not Started |       |     |

---

## 7) Risks & Mitigations

| Risk ID | Description                             | Severity | Likelihood | Mitigation                                  | Owner | Status |
| ------- | --------------------------------------- | -------- | ---------- | ------------------------------------------- | ----- | ------ |
| RSK-001 | GPT OCR misreads low-quality scans      | High     | Med        | Add confidence scoring & optional review UI |       | Open   |
| RSK-002 | Schema mismatch with future ERP systems | Med      | Med        | Version schema, add mapping layer           |       | Open   |

---

## 8) Future Considerations

* **Add authentication & persistence** for multi-user environments.
* **Support for receipts & purchase orders.**
* **Fine-tuning / few-shot GPT examples** for accuracy.
* **Add export connectors (QuickBooks, NetSuite, SAP).**

---

## 9) Changelog

| Version | Date       | Change        | Author        |
| ------- | ---------- | ------------- | ------------- |
| 1.0     | 2025-10-20 | Initial draft | James Simmons |
