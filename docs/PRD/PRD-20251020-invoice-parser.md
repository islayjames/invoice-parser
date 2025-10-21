# Product Requirements Document (PRD) — Invoice Parsing API & UI Prototype

## 0) Meta

* **PRD ID:** PRD-20251020-INVOICE-PARSER
* **Version:** 1.1
* **Status:** Refined
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
* **Constraints:** Stateless v1; limited to invoices ≤ 5MB; response time ≤ 20s per document; clean PDF invoices only for v1 (scanned/handwritten deferred to v2).
* **Non-Goals:** Vendor-specific template handling, data persistence, or user authentication in v1.

---

## 2) Scope Overview

* **Core Use Cases:**

  1. User uploads invoice file (PDF, image, or text).
  2. Backend uses GPT-4o to extract structured data via a unified schema.
  3. Frontend displays parsed output in structured UI with header, summary, and payment details nicely formatted (similar to traditional invoice layout). User can toggle to view formatted JSON for full details.
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
* **Supported Formats:**
  * **PDF**: Any PDF document
  * **Images**: JPEG/JPG, PNG, TIFF, BMP, WebP, HEIC/HEIF, GIF
  * **Text**: .txt, .md
* **Upload Methods:** Click to browse/select file, drag-and-drop
* **Processing Mode:** Synchronous (user waits up to 20s for response)
* **Concurrency:** Single file processing only (one invoice at a time)
* **Main Flow:** Receive file → Validate (MIME type, size, extension) → Pass to GPT-4o parser → Return results
* **Telemetry:** upload.count, upload.size.avg, processing_time_ms
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
* **Model Configuration:**
  * **Model**: Latest GPT-4o (auto-upgrade enabled)
  * **Temperature**: 0.4 (balanced factual extraction)
  * **Language Support**: English primary; best-effort support for Spanish invoices with translation
  * **Date Format**: Assume US format (MM/DD/YYYY) by default
* **Retry Logic**: 3 retries with exponential backoff on API failures
* **Line Items**: Maximum 50 line items per invoice
* **Success Metrics:** ≥90% field accuracy vs ground truth (manual validation on clean PDF test dataset).
* **Priority:** Must

**Acceptance Criteria (Gherkin)**

```gherkin
Scenario: Parse invoice with unknown layout
  Given an invoice of arbitrary vendor format
  When processed by GPT-4o
  Then the system returns structured JSON following the invoice schema
```

#### REQ-003 — Output Schema Enforcement & Confidence Scoring

* **Description:** Validate and normalize GPT output against canonical schema with field-level confidence scoring.
* **Schema:** Supplier, Customer, Invoice summary, Line items, Metadata.
* **Critical Fields** (must be ≥50% confidence or reject parsing):
  * `supplier.name`
  * `invoice.number`
  * `invoice.issue_date`
  * `invoice.due_date`
  * `invoice.total`
  * `customer.name`
* **Confidence Logic:**
  * **Reject**: If any critical field has confidence <50%
  * **Warning**: If any critical field has confidence 50-90%, or if any non-critical field is present with <90% confidence
  * **Success**: All critical fields ≥90% confidence and all present non-critical fields ≥90% confidence
* **Optional Fields**: Line items and non-critical fields may be empty without triggering warnings
* **Currency Default**: Assume "USD" if currency field not explicitly detected
* **Priority:** Must

#### REQ-004 — React UI Prototype

* **Description:** Stateless UI with upload box and structured data viewer.
* **Display Modes:**
  * **Default View**: Nicely formatted invoice display with table-based layout showing header, summary, and payment details (similar to traditional invoice format - reference: https://www.kiwili.com/wp-content/uploads/2018/07/Invoice-software-Kiwili-1.png)
  * **Raw View**: Toggle to view formatted/pretty-printed JSON with full field-level confidence scores
* **Upload Interface:**
  * Click to browse/select file button
  * Drag-and-drop zone
  * Loading spinner during processing (synchronous, up to 20s wait)
* **Features:**
  * One-click copy full JSON (including metadata and confidence scores) to clipboard
  * Warning indicator if confidence scores are low (general warning, not field-specific in UI for v1)
  * Error display area for failed parses
* **Platform Support:**
  * Desktop only (no mobile/tablet optimization required for v1)
  * Browser support: Chrome and Edge
* **Design Level:** Table-based layout with basic styling (minimal/moderate CSS)
* **Priority:** Should
* **Status:** Not Started

#### REQ-005 — Deployment

* **Description:** Deploy backend and frontend to production hosting platforms.
* **Platform Targets:**
  * **Frontend**: Vercel
  * **Backend**: Railway
* **Environment Management:**
  * **Local Development**: `.env` files for API keys and configuration
  * **Production**: Platform environment variables (Vercel env variables, Railway secrets)
* **Required Environment Variables:**
  * `OPENAI_API_KEY` - GPT-4o API access
  * Backend URL configuration for CORS
* **Audience**: Internal stakeholders (demo/prototype)
* **Priority:** Should

---

## 4) Non-Functional Requirements

| NFR ID  | Category    | Statement (Measurable)                   | Metric/Method         | Priority | Status      |
| ------- | ----------- | ---------------------------------------- | --------------------- | -------- | ----------- |
| NFR-001 | Performance | Parse ≤20s for files ≤5MB                | Integration test      | Must     | Not Started |
| NFR-002 | Reliability | 99% uptime (aspirational goal for v1)    | Basic application logs| Should   | Not Started |
| NFR-003 | Security    | Validate input (MIME, size, extension)   | Input validation tests| Must     | Not Started |
| NFR-004 | Privacy     | Do not persist invoice data              | Code review           | Must     | Not Started |
| NFR-005 | Observability | Include processing time in API response| Response metadata     | Should   | Not Started |

### 4.1) Security & Input Validation Details (NFR-003)

**Minimal Security for MVP:**
* File size validation: Reject files >5MB
* MIME type whitelist: PDF, JPEG/JPG, PNG, TIFF, BMP, WebP, HEIC/HEIF, GIF, TXT, MD
* File extension validation: Basic check that extension matches expected MIME type
* **Deferred to v2**: Virus scanning, advanced corruption detection, rate limiting

**Data Handling (NFR-004):**
* Process files in memory where possible
* Temporary disk storage allowed during processing if required by libraries
* Immediate deletion of all file data after API response sent
* No logging of invoice content (metadata logging only)

### 4.2) Error Handling Strategy

**Error Scenarios to Handle:**
* File too large (>5MB) → HTTP 413 Payload Too Large
* Unsupported file format → HTTP 415 Unsupported Media Type
* Corrupted/unreadable file → HTTP 422 Unprocessable Entity
* GPT-4o API timeout (after retries) → HTTP 504 Gateway Timeout
* GPT-4o rate limit exceeded (after retries) → HTTP 429 Too Many Requests
* Critical field confidence <50% → HTTP 422 with confidence score details
* No invoice data detected → HTTP 422 Unprocessable Entity
* Network/connection errors → HTTP 503 Service Unavailable

**Error Response Format:**
```json
{
  "error": {
    "code": "CONFIDENCE_TOO_LOW",
    "message": "Unable to extract required fields with sufficient confidence",
    "details": {
      "failed_fields": ["supplier.name", "invoice.number"],
      "confidence_scores": { "supplier.name": 0.42, "invoice.number": 0.38 }
    }
  }
}
```

**UI Error Handling:**
* Display error message in dedicated error display area
* No correction mechanism in v1 (simple rejection)
* User must re-upload with different/better quality file

---

## 5) Data & Interfaces

### Invoice Schema v1.1

```json
{
  "supplier": {
    "name": { "value": "string", "confidence": "number" },
    "address": { "value": "string", "confidence": "number" },
    "phone": { "value": "string", "confidence": "number" },
    "email": { "value": "string", "confidence": "number" },
    "tax_id": { "value": "string", "confidence": "number" }
  },
  "customer": {
    "name": { "value": "string", "confidence": "number" },
    "address": { "value": "string", "confidence": "number" },
    "account_id": { "value": "string", "confidence": "number" }
  },
  "invoice": {
    "number": { "value": "string", "confidence": "number" },
    "issue_date": { "value": "YYYY-MM-DD", "confidence": "number" },
    "due_date": { "value": "YYYY-MM-DD", "confidence": "number" },
    "currency": { "value": "string", "confidence": "number", "default": "USD" },
    "subtotal": { "value": "number", "confidence": "number" },
    "tax": { "value": "number", "confidence": "number" },
    "total": { "value": "number", "confidence": "number" },
    "payment_terms": { "value": "string", "confidence": "number" },
    "po_number": { "value": "string", "confidence": "number" }
  },
  "line_items": [
    {
      "sku": { "value": "string", "confidence": "number" },
      "description": { "value": "string", "confidence": "number" },
      "quantity": { "value": "number", "confidence": "number" },
      "unit_price": { "value": "number", "confidence": "number" },
      "discount": { "value": "number", "confidence": "number" },
      "tax_rate": { "value": "number", "confidence": "number" },
      "total": { "value": "number", "confidence": "number" }
    }
  ],
  "meta": {
    "source_file_name": "string",
    "source_format": "pdf|image|text",
    "model_version": "string",
    "extraction_time": "ISO 8601",
    "processing_time_ms": "number",
    "overall_confidence": "number",
    "warning": "string|null"
  }
}
```

**Schema Notes:**
* All extracted fields include field-level confidence scores (0.0 to 1.0)
* Maximum 50 line items per invoice
* `meta.warning`: Populated if any critical field has confidence 50-90%, or non-critical fields <90%
* `meta.overall_confidence`: Minimum confidence score across all critical fields
* Currency defaults to "USD" if not detected

---

## 6) Testing Strategy & Success Criteria

### 6.1) Test Dataset

**Composition:**
* **Size**: 10-20 clean PDF invoice samples
* **Focus**: Various layouts and vendor formats (different invoice templates)
* **Language**: Primarily English (v1 focus)
* **Quality**: High-quality, typed text PDFs only (no scanned/handwritten invoices)

**Dataset Purpose:**
* Validate ≥90% field extraction accuracy target
* Test diverse invoice layouts and formats
* Establish baseline performance metrics
* Regression testing for future changes

### 6.2) Definition of Done (v1 Launch)

**Must-Have Criteria:**
- [ ] Backend API successfully parses clean PDF invoices with 90%+ accuracy (validated against test dataset)
- [ ] Frontend displays formatted invoice view with table-based layout
- [ ] JSON toggle displays formatted/pretty-printed raw data with confidence scores
- [ ] Copy to clipboard functionality works reliably
- [ ] Error handling displays meaningful messages in UI error area
- [ ] Deployed to Vercel (frontend) and Railway (backend)
- [ ] Successfully demos with test dataset (10-20 invoices)

**Testing Coverage:**
* **Unit Tests**: ≥80% coverage for backend parsing logic
* **Integration Tests**: End-to-end API flow with GPT-4o integration
* **E2E Tests**: Frontend upload → parse → display → copy workflow
* **Validation Tests**: Input validation (file size, MIME type, extension)
* **Performance Tests**: Verify ≤20s parse time for sample invoices

### 6.3) Success Metrics

**Primary Metrics:**
* Field extraction accuracy: ≥90% on test dataset
* Upload success rate: ≥95%
* Parse time: ≤20s per file (5MB max)
* Critical field confidence: ≥50% (or rejection)

**Demo Audience:**
* Internal stakeholders
* Purpose: Proof of concept / technical demonstration

## 7) Implementation Plan & Status

| Work Item   | Coverage (Req/NFR IDs) | Priority | Status      | Owner | ETA |
| ----------- | ---------------------- | -------- | ----------- | ----- | --- |
| Backend API | REQ-001–REQ-003        | Must     | Not Started |       |     |
| Frontend UI | REQ-004                | Should   | Not Started |       |     |
| Deployment  | REQ-005, NFR-001       | Should   | Not Started |       |     |
| Test Dataset| Testing Strategy       | Must     | Not Started |       |     |

---

## 8) Risks & Mitigations

| Risk ID | Description                             | Severity | Likelihood | Mitigation                                  | Owner | Status |
| ------- | --------------------------------------- | -------- | ---------- | ------------------------------------------- | ----- | ------ |
| RSK-001 | GPT OCR misreads low-quality scans      | High     | Med        | Add confidence scoring & optional review UI |       | Open   |
| RSK-002 | Schema mismatch with future ERP systems | Med      | Med        | Version schema, add mapping layer           |       | Open   |

---

## 9) Future Considerations

* **Add authentication & persistence** for multi-user environments.
* **Support for receipts & purchase orders.**
* **Fine-tuning / few-shot GPT examples** for accuracy.
* **Add export connectors (QuickBooks, NetSuite, SAP).**

---

## 10) Changelog

| Version | Date       | Change                                                                                     | Author        |
| ------- | ---------- | ------------------------------------------------------------------------------------------ | ------------- |
| 1.0     | 2025-10-20 | Initial draft                                                                              | James Simmons |
| 1.1     | 2025-10-20 | Refined via /refine-prd: Added file format specs, UI/UX details, confidence scoring logic, error handling, GPT-4o config, deployment specs, testing strategy, and comprehensive Definition of Done | James Simmons |
