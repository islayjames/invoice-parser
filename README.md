# Invoice Parser - AI-Powered Document Processing API

AI-powered API and UI prototype for parsing invoices of any format (PDF, image, text) into structured, machine-readable JSON suitable for ERP and finance system ingestion.

## Project Status

**Phase**: Sprint 1 - Foundation & Setup (In Progress)
**Version**: v1.0 (Prototype)
**Last Updated**: 2025-10-20

```yaml
✅ PRD Complete: docs/PRD/PRD-20251020-invoice-parser.md
✅ TRD Complete: docs/TRD/TRD-20251020-invoice-parser.md
🔄 Sprint 1 In Progress: Environment setup and test dataset creation
⏳ Sprint 2-5: Backend, Frontend, Testing, Deployment
```

## Overview

### Problem
Businesses receive invoices in diverse formats—PDFs, images, emails, and text—with no consistent structure, creating bottlenecks in financial data ingestion.

### Solution
AI-powered API leveraging GPT-4o to extract structured data from arbitrary invoice formats, enabling seamless integration with ERP and finance systems.

### Target Users
- Finance operations engineers
- Accountants and AP/AR teams
- ERP system integrators
- Financial automation developers

## Core Features (v1)

### REQ-001: Invoice Upload Endpoint
- **POST /api/parse** - Accept PDF, image, or text files
- File size limit: 5MB
- MIME type validation for security
- Stateless processing (no persistence)

### REQ-002: GPT-4o Semantic Parser
- Unified processing for all file formats
- Robust OCR for images and scanned PDFs
- Semantic understanding for arbitrary layouts
- Target: 90%+ field extraction accuracy

### REQ-003: Structured Output Schema
- Comprehensive invoice data model
- Supplier, customer, and invoice details
- Line item extraction with quantities and pricing
- Metadata including confidence scoring

### REQ-004: React UI Prototype
- Simple file upload interface (drag-and-drop)
- Real-time parsing progress indicator
- Structured display: Header, summary, payment details (nicely formatted)
- YAML viewer for full invoice details
- Copy/export functionality

### REQ-005: Vercel Deployment
- Backend: FastAPI on Railway/Vercel
- Frontend: React on Vercel
- Production-ready infrastructure
- 99% uptime target

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Engine**: OpenAI GPT-4o Vision API
- **Validation**: Pydantic for schema enforcement
- **Testing**: Pytest (unit + integration)

### Frontend
- **Framework**: React
- **Styling**: Tailwind CSS (planned)
- **State Management**: React hooks (stateless)
- **Testing**: Jest + React Testing Library

### Infrastructure
- **Deployment**: Vercel (frontend), Railway/Vercel (backend)
- **Monitoring**: Vercel Analytics + custom health checks
- **CI/CD**: GitHub Actions (planned)

## Invoice Schema (v1.1)

```json
{
  "supplier": {
    "name": "string",
    "address": "string",
    "phone": "string",
    "email": "string",
    "tax_id": "string"
  },
  "customer": {
    "name": "string",
    "address": "string",
    "account_id": "string"
  },
  "invoice": {
    "number": "string",
    "issue_date": "YYYY-MM-DD",
    "due_date": "YYYY-MM-DD",
    "currency": "string",
    "subtotal": "number",
    "tax": "number",
    "total": "number",
    "payment_terms": "string",
    "po_number": "string"
  },
  "line_items": [
    {
      "sku": "string",
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "discount": "number",
      "tax_rate": "number",
      "total": "number"
    }
  ],
  "meta": {
    "source_file_name": "string",
    "source_format": "pdf|image|text",
    "confidence_score": "number",
    "model_version": "string",
    "extraction_time": "ISO 8601"
  }
}
```

## Performance Targets

### Functional Requirements
- **Upload Success Rate**: ≥95%
- **Field Extraction Accuracy**: ≥90%
- **Parse Time**: ≤20s per file (≤5MB)

### Non-Functional Requirements
- **API Uptime**: 99% availability
- **Security**: MIME validation, size limits, no data persistence
- **Privacy**: Zero invoice data retention (NFR-004)

## Project Structure (Planned)

```
invoice-parser/
├── docs/
│   ├── PRD/
│   │   └── PRD-20251020-invoice-parser.md
│   └── TRD/
│       └── invoice-parser-trd.md (to be created)
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application
│   │   ├── routers/
│   │   │   └── parse.py             # /api/parse endpoint
│   │   ├── services/
│   │   │   └── gpt4o_parser.py      # GPT-4o integration
│   │   └── schemas/
│   │       └── invoice.py           # Pydantic models
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   └── JSONViewer.jsx
│   │   └── App.jsx
│   └── package.json
├── .env.example
├── vercel.json
├── README.md
└── CLAUDE.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key with GPT-4o access

### Installation

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Add your OPENAI_API_KEY

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local  # Set VITE_API_BASE_URL=http://localhost:8000

# Run development server
npm run dev
```

#### Running Tests

```bash
# Backend tests
cd backend
pytest                      # Run all tests
pytest --cov               # Run with coverage report

# Frontend tests
cd frontend
npm test                   # Run Jest tests
```

## API Usage (Planned)

### Parse Invoice Endpoint

```bash
POST /api/parse
Content-Type: multipart/form-data

# Example request
curl -X POST http://localhost:8000/api/parse \
  -F "file=@invoice.pdf" \
  -H "Content-Type: multipart/form-data"

# Example response
{
  "supplier": {
    "name": "Acme Corp",
    "address": "123 Main St, City, State 12345",
    ...
  },
  "invoice": {
    "number": "INV-2025-001",
    "total": 1250.00,
    ...
  },
  "meta": {
    "confidence_score": 0.94,
    "model_version": "gpt-4o-2024-05-13",
    "extraction_time": "2025-10-20T14:32:10Z"
  }
}
```

## Development Workflow

### AI-Augmented Development
This project uses an AI-augmented development process with specialized sub-agents:

- **tech-lead-orchestrator**: Creates TRD and coordinates implementation
- **backend-developer**: Implements FastAPI and GPT-4o integration
- **frontend-developer**: Builds React UI components
- **test-runner**: Validates test coverage and NFRs
- **code-reviewer**: Ensures security and quality standards
- **devops-engineer**: Handles deployment and infrastructure

See [CLAUDE.md](CLAUDE.md) for detailed orchestration workflows.

### Current Phase: Sprint 1 - Foundation & Setup

1. ✅ **PRD Complete**: Requirements and scope defined
2. ✅ **TRD Complete**: Technical architecture and task breakdown
3. 🔄 **Sprint 1 (Days 1-2)**: Environment setup and test dataset
4. ⏳ **Sprint 2-3 (Days 3-7)**: Backend and Frontend implementation
5. ⏳ **Sprint 4-5 (Days 8-10)**: Testing and Deployment

### Next Steps

```bash
# 1. Create Technical Requirements Document
"Create TRD from the invoice parser PRD"

# 2. Implement backend API
/implement-trd

# 3. Deploy to production
"Deploy invoice parser to Vercel and Railway"
```

## Testing Strategy

### Unit Tests
- File upload validation
- Schema enforcement
- GPT-4o response parsing
- Error handling

### Integration Tests
- End-to-end parsing flow
- GPT-4o API integration
- Performance validation (≤10s)
- Accuracy testing (≥90%)

### E2E Tests (Playwright)
- UI file upload flow
- JSON viewer rendering
- Error state handling
- Cross-browser compatibility

## Security Considerations

### Input Validation (NFR-003)
- MIME type whitelist (PDF, image formats, text)
- File size enforcement (≤5MB)
- Path traversal prevention
- Malformed file rejection

### Privacy Compliance (NFR-004)
- Zero data persistence (in-memory processing only)
- No invoice content logging
- Temporary file cleanup
- API key security (environment variables)

### API Security
- CORS configuration
- Rate limiting (planned for v2)
- HTTPS enforcement
- Error message sanitization

## Known Limitations (v1)

### Scope Constraints
- No authentication or user management
- No invoice history or storage
- No vendor-specific template handling
- No batch processing (single file at a time)

### Performance Trade-offs
- GPT-4o API latency (5-10s typical)
- File size limit (5MB) for processing speed
- Stateless design (no caching)

### Accuracy Considerations
- 90%+ accuracy target (not 100%)
- Low-quality scans may reduce accuracy
- Multilingual invoices require testing
- Handwritten invoices not supported in v1

## Risks & Mitigations

### RSK-001: GPT OCR Misreads Low-Quality Scans
- **Severity**: High
- **Mitigation**: Confidence scoring, user feedback UI, quality guidelines
- **Testing**: Diverse sample dataset validation

### RSK-002: Schema Mismatch with ERP Systems
- **Severity**: Medium
- **Mitigation**: Versioned schema, extensibility planning, mapping layer (v2)
- **Documentation**: Schema evolution guide

## Future Roadmap (v2+)

### Authentication & Multi-User Support
- User accounts and API keys
- Invoice history and storage
- Team collaboration features

### Enhanced Accuracy
- Fine-tuning with domain-specific examples
- Few-shot learning for vendor templates
- Human-in-the-loop validation UI

### Extended Document Support
- Receipts and purchase orders
- Packing slips and delivery notes
- Multi-page invoice handling

### ERP Integrations
- QuickBooks Online connector
- NetSuite integration
- SAP Business One API
- Custom webhook support

### Advanced Features
- Batch processing API
- Async processing with webhooks
- Duplicate invoice detection
- Currency conversion

## Documentation

- **[PRD](docs/PRD/PRD-20251020-invoice-parser.md)**: Product requirements and specifications
- **[TRD](docs/TRD/)**: Technical requirements and architecture (to be created)
- **[CLAUDE.md](CLAUDE.md)**: AI-augmented development guide and agent orchestration
- **API Docs**: OpenAPI/Swagger documentation (after implementation)

## Contributing

This is a prototype project following an AI-augmented development methodology. See [CLAUDE.md](CLAUDE.md) for agent orchestration workflows and contribution guidelines.

## License

TBD

## Contact

**Project Owner**: James Simmons
**Email**: james.simmons@fortiumpartners.com
**PRD ID**: PRD-20251020-INVOICE-PARSER

---

**Status**: Phase 1 - Planning & Architecture
**Next Milestone**: TRD Creation & Approval
**Target Launch**: 2 weeks from TRD approval
