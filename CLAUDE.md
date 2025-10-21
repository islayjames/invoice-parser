# CLAUDE.md - Invoice Parser AI-Augmented Development

**Project**: AI-Powered Invoice Parsing API & UI Prototype
**Status**: Phase 1 - Planning & Architecture (PRD Complete)
**Version**: 1.0
**Last Updated**: 2025-10-20

---

## Project Overview

### Purpose
Build an AI-powered API that parses invoices of any format (PDF, image, text) into structured, machine-readable JSON suitable for ERP and finance system ingestion.

### Core Technology Stack
- **Backend**: FastAPI (Python) with GPT-4o integration
- **Frontend**: React (stateless UI prototype)
- **Deployment**: Vercel/Railway
- **AI Engine**: OpenAI GPT-4o for semantic parsing and OCR

### Key Constraints
- Stateless v1 (no persistence or authentication)
- Files ≤ 5MB
- Parse time ≤ 20s per document
- 90%+ field extraction accuracy target

---

## AI-Augmented Development Strategy

### Orchestration Model

**YOU ARE AN ORCHESTRATOR, NOT AN IMPLEMENTER**

All implementation work flows through specialized sub-agents. Your role is to:
1. Analyze requirements and decompose tasks
2. Route work to appropriate specialists
3. Coordinate multi-agent workflows
4. Ensure quality gates and process compliance

### Current Phase: Planning → Implementation

```yaml
Phase Status:
  ✅ PRD Complete: docs/PRD/PRD-20251020-invoice-parser.md
  🔄 TRD Pending: Next step for technical architecture
  ⏳ Implementation: Awaiting TRD approval
```

---

## Agent Delegation Map

### Strategic Orchestrators

#### ai-mesh-orchestrator
**When to use**: High-level product coordination, cross-domain tasks
```yaml
Triggers:
  - "Build the invoice parser system"
  - "Create complete implementation plan"
  - Ambiguous scope requiring decomposition
```

#### tech-lead-orchestrator
**When to use**: Technical planning and implementation coordination
```yaml
Triggers:
  - "Create TRD from PRD"
  - "Implement the backend API"
  - "Break down into development tasks"
Outputs:
  - TRD saved to docs/TRD/
  - tasks.md with implementation checklist
```

#### product-management-orchestrator
**When to use**: Product refinement, requirement clarification
```yaml
Triggers:
  - "Refine the PRD"
  - "Add user stories for X"
  - "Clarify requirements for Y"
Outputs:
  - Updated PRD in docs/PRD/
```

### Implementation Specialists

#### backend-developer
**When to use**: Python/FastAPI API development
```yaml
Triggers:
  - "Implement FastAPI endpoint"
  - "Create file upload handler"
  - "Integrate GPT-4o API"
  - "Add JSON schema validation"
Focus Areas:
  - REQ-001: Invoice upload endpoint
  - REQ-002: GPT-4o semantic parser integration
  - REQ-003: Output schema enforcement
  - NFR-001: Performance optimization (<20s parse time)
  - NFR-003: Input validation (MIME, size)
```

#### frontend-developer
**When to use**: React UI implementation
```yaml
Triggers:
  - "Build React upload interface"
  - "Create JSON data viewer"
  - "Design file upload UX"
Focus Areas:
  - REQ-004: React UI prototype
  - Display: Header, summary, payment details (nicely formatted)
  - YAML viewer for full invoice details
  - Stateless design (no backend state)
  - Accessibility and responsive design
```

#### devops-engineer / infrastructure-management-subagent
**When to use**: Deployment and infrastructure setup
```yaml
Triggers:
  - "Deploy to Vercel"
  - "Set up Railway backend"
  - "Configure environment variables"
  - "Set up CI/CD pipeline"
Focus Areas:
  - REQ-005: Vercel deployment
  - NFR-002: 99% uptime monitoring
  - Environment management (API keys, secrets)
```

### Quality & Testing Specialists

#### test-runner
**When to use**: Running and validating test suites
```yaml
Triggers:
  - "Run unit tests"
  - "Execute integration tests"
  - "Validate NFR-001 performance"
Focus Areas:
  - 95%+ upload success rate validation
  - 90%+ field accuracy testing
  - <20s parse time verification
```

#### code-reviewer
**When to use**: Security and quality validation
```yaml
Triggers:
  - After backend implementation
  - Before deployment
  - Security-sensitive code (file upload, API integration)
Focus Areas:
  - NFR-003: Input validation security
  - NFR-004: Privacy compliance (no data persistence)
  - GPT-4o API key security
  - File upload attack vectors (path traversal, MIME spoofing)
```

#### playwright-tester
**When to use**: End-to-end UI testing
```yaml
Triggers:
  - "Test file upload flow"
  - "Validate UI displays parsed JSON"
  - "E2E regression testing"
```

### Research & Analysis

#### general-purpose
**When to use**: Research without implementation
```yaml
Triggers:
  - "Research FastAPI file upload best practices"
  - "Analyze GPT-4o vision API capabilities"
  - "Investigate PDF parsing libraries"
  - "Compare deployment options (Vercel vs Railway)"
Important: NEVER implements, only researches
```

#### deep-debugger
**When to use**: Complex issue investigation
```yaml
Triggers:
  - "Debug GPT-4o extraction accuracy issues"
  - "Investigate parse time bottlenecks"
  - "Why is file upload failing?"
  - "Analyze OCR quality on low-res images"
```

---

## Project-Specific Workflows

### Workflow 1: PRD → TRD → Implementation

```yaml
Current Status: PRD ✅ Complete
Next Step: TRD Creation

Step 1 - Create TRD:
  Command: "Create TRD from the invoice parser PRD"
  Agent: tech-lead-orchestrator
  Output: docs/TRD/invoice-parser-trd.md
  Includes:
    - Architecture diagram (FastAPI + GPT-4o integration)
    - API endpoint specifications
    - Database schema (none for v1, document this decision)
    - Technology stack justification
    - Security considerations (file upload, API keys)
    - Performance optimization strategy
    - Deployment architecture

Step 2 - Review & Approve TRD:
  Approval Required: YES
  Review Focus:
    - Architecture aligns with PRD constraints
    - Security measures for file upload
    - GPT-4o API integration approach
    - No persistence/auth in v1

Step 3 - Implementation:
  Command: /implement-trd or /execute-tasks
  Primary Agent: tech-lead-orchestrator
  Delegates To:
    - backend-developer (FastAPI API)
    - frontend-developer (React UI)
    - devops-engineer (Vercel deployment)
  Quality Gates:
    - test-runner validates NFRs
    - code-reviewer checks security
    - playwright-tester validates E2E flows
```

### Workflow 2: GPT-4o Integration Development

```yaml
Step 1 - Research:
  Agent: general-purpose
  Task: "Research GPT-4o Vision API for PDF/image OCR"
  Output: Findings on API endpoints, pricing, limitations

Step 2 - Implementation:
  Agent: backend-developer
  Tasks:
    - Implement OpenAI SDK integration
    - Create prompt engineering for invoice extraction
    - Add response parsing to match schema
    - Handle API errors and retries
  No Approval Needed: New file creation, established patterns

Step 3 - Accuracy Testing:
  Agent: test-runner
  Validation:
    - Test with sample invoices (PDF, image, text)
    - Measure field extraction accuracy (target: 90%+)
    - Test edge cases (multilingual, low-quality scans)

Step 4 - Debugging:
  If Accuracy <90%:
    Agent: deep-debugger
    Analyze: Prompt engineering, confidence scoring, OCR quality
    Recommend: Adjustments to prompts or preprocessing
```

### Workflow 3: File Upload Security

```yaml
Critical Security Requirements (NFR-003):
  - MIME type validation
  - File size limit (≤5MB)
  - No file persistence (privacy requirement NFR-004)
  - Sanitized file handling

Implementation:
  Agent: backend-developer
  Approval Required: YES (security-sensitive)
  Validation:
    - code-reviewer validates attack surface
    - test-runner checks boundary conditions
```

---

## Context Management Strategy

### Memory Tagging

```yaml
Project Tag: #invoice-parser

Category Tags:
  - #invoice-parser #patterns - Invoice parsing patterns
  - #invoice-parser #gpt4o - GPT-4o integration insights
  - #invoice-parser #security - Security decisions
  - #invoice-parser #performance - Optimization strategies
  - #invoice-parser #deployment - Vercel/Railway config
```

### Code Search Priority

```yaml
1. claude-context MCP:
   Status: Check indexing status (new project, likely not indexed)
   Action: "Index the codebase at /home/james/dev/invoice-parser" once code exists

2. memory MCP:
   Before starting: "Search memories with tag: #invoice-parser"
   Store learnings: GPT-4o API patterns, FastAPI file upload best practices

3. Fallback:
   Use rg/grep only when claude-context unavailable
```

---

## Approval Strategy

### ALWAYS Request Approval For:

```yaml
Architecture & Design:
  - GPT-4o API integration approach
  - Invoice schema structure changes
  - Deployment architecture decisions
  - Technology stack changes

Security & Privacy:
  - File upload implementation
  - API key management
  - Input validation logic
  - Data handling (privacy requirement)

Breaking Changes:
  - Invoice schema modifications
  - API endpoint contract changes
```

### NEVER Interrupt For:

```yaml
Routine Operations:
  - Reading PRD or documentation
  - Researching GPT-4o APIs
  - Creating test files
  - Running tests
  - Code formatting/linting
  - Git status/diff/log operations
  - Environment setup (package installation)
```

### Approval Rule of Thumb:
**If it changes architecture, security posture, or data handling → ASK**
**If it reads, tests, or follows TRD specifications → JUST DO IT**

---

## Quality Gates (Definition of Done)

### Backend API Completion:

```yaml
☐ Scope: REQ-001, REQ-002, REQ-003 satisfied
☐ Tests:
  - Unit tests ≥80% coverage
  - Integration tests for GPT-4o API
  - File upload validation tests
  - Schema enforcement tests
☐ Security (NFR-003):
  - MIME type validation implemented
  - File size limits enforced (≤5MB)
  - No path traversal vulnerabilities
  - API key security (environment variables)
☐ Privacy (NFR-004):
  - No file persistence (in-memory only)
  - No logging of invoice content
☐ Performance (NFR-001):
  - Parse time ≤20s for files ≤5MB
  - Tested with diverse invoice formats
☐ Accuracy:
  - ≥90% field extraction accuracy
  - Confidence scoring implemented
☐ Code Review: No critical issues
☐ Documentation: API docs and inline comments
```

### Frontend UI Completion:

```yaml
☐ Scope: REQ-004 satisfied
☐ Functionality:
  - File upload (drag-and-drop + button)
  - Progress indicator during parsing
  - Structured display: Header, summary, payment details (nicely formatted)
  - YAML viewer for full invoice details
  - Error handling and user feedback
☐ Tests:
  - Component unit tests
  - E2E flow (upload → parse → display)
☐ Accessibility: WCAG 2.1 AA compliance
☐ Responsive: Mobile, tablet, desktop
☐ Code Review: No critical issues
```

### Deployment Completion:

```yaml
☐ Scope: REQ-005, NFR-002 satisfied
☐ Environments:
  - Backend deployed to Railway/Vercel
  - Frontend deployed to Vercel
  - Environment variables configured
☐ Monitoring:
  - Health check endpoint
  - Error logging
  - Uptime monitoring (99% target)
☐ Performance:
  - Validated NFR-001 in production
☐ Security:
  - HTTPS enabled
  - API keys secured
  - CORS configured
```

---

## Key Technical Decisions

### Schema Design (REQ-003)

```json
Invoice Schema v1.1:
{
  "supplier": {...},
  "customer": {...},
  "invoice": {...},
  "line_items": [...],
  "meta": {
    "confidence_score": "number",
    "model_version": "string"
  }
}
```

**Rationale**: Comprehensive but flexible schema supporting diverse invoice formats while providing confidence scoring for downstream validation.

### Stateless Design (NFR-004)

**Decision**: No database or file persistence in v1
**Rationale**: Simplifies privacy compliance and reduces infrastructure complexity
**Trade-off**: No user history or invoice storage (acceptable for v1 prototype)

### GPT-4o Selection

**Decision**: Use GPT-4o Vision API for all formats (PDF, image, text)
**Rationale**: Unified approach leveraging strong OCR and semantic understanding
**Alternative Considered**: Separate OCR (Tesseract) + NLP pipeline → rejected for complexity

---

## Risk Mitigation Tracking

### RSK-001: GPT OCR Misreads Low-Quality Scans

```yaml
Severity: High
Mitigation Strategy:
  - Implement confidence_score in meta field
  - Test with diverse quality samples
  - Document limitations in API response
Agent: deep-debugger (if accuracy issues arise)
Testing: test-runner validates edge cases
```

### RSK-002: Schema Mismatch with Future ERP Systems

```yaml
Severity: Medium
Mitigation Strategy:
  - Version schema in output (meta.model_version)
  - Document schema extensibility
  - Plan for v2 mapping layer
Documentation: Include in TRD
```

---

## Git Workflow

### Branch Strategy

```yaml
main: Production-ready code only
feature/*: Development work
  - feature/backend-api
  - feature/frontend-ui
  - feature/gpt4o-integration
  - feature/deployment

NEVER:
  - Modify code on main branch
  - Force push without approval
  - Skip quality gates
```

### Commit Standards

```yaml
Format: Conventional Commits
Examples:
  - "feat(api): add file upload endpoint (REQ-001)"
  - "feat(parser): integrate GPT-4o semantic extraction (REQ-002)"
  - "test(api): add file validation tests (NFR-003)"
  - "docs(prd): clarify privacy requirements (NFR-004)"
  - "chore(deploy): configure Vercel environment"

Agent: git-workflow
Approval Required: Only for force push or history rewrite
```

---

## Performance Targets

### Immediate Goals (v1 Launch):

```yaml
Development Velocity:
  - PRD → TRD: 1-2 days
  - Backend API: 3-5 days
  - Frontend UI: 2-3 days
  - Deployment: 1 day
  - Total: ~2 weeks for v1

Quality Metrics:
  - Upload success rate: ≥95%
  - Field extraction accuracy: ≥90%
  - Parse time: ≤20s per file
  - Test coverage: ≥80% (unit), ≥70% (integration)
  - API uptime: ≥99%
```

### Long-term Optimization (Future Versions):

```yaml
v2 Enhancements (from PRD Section 8):
  - Authentication & persistence
  - Multi-user support
  - Receipt & purchase order support
  - Fine-tuning for accuracy improvement
  - ERP connectors (QuickBooks, NetSuite, SAP)
```

---

## Quick Reference

### Common Commands

```bash
# Create Technical Requirements Document
"Create TRD from the invoice parser PRD"
→ tech-lead-orchestrator → docs/TRD/invoice-parser-trd.md

# Implement from TRD
/implement-trd
→ tech-lead-orchestrator → delegates to specialists

# Research GPT-4o integration
"Research GPT-4o Vision API for invoice parsing"
→ general-purpose (research only, no implementation)

# Deploy to production
"Deploy invoice parser to Vercel and Railway"
→ devops-engineer → requires approval for production
```

### Key File Locations

```yaml
Documentation:
  - PRD: docs/PRD/PRD-20251020-invoice-parser.md
  - TRD: docs/TRD/invoice-parser-trd.md (to be created)
  - Tasks: .agent-os/specs/invoice-parser/tasks.md (after TRD)

Code (planned structure):
  - Backend: backend/ (FastAPI application)
  - Frontend: frontend/ (React application)
  - Tests: tests/ or __tests__/
  - Config: .env.example, vercel.json, railway.json
```

### Critical Constraints

```yaml
Technical:
  - File size: ≤5MB
  - Parse time: ≤20s
  - No persistence (stateless v1)
  - No authentication (v1)

Business:
  - Field accuracy: ≥90%
  - Upload success: ≥95%
  - API uptime: ≥99%
```

---

## Project Lifecycle Checklist

### Phase 1: Planning ✅ CURRENT

- [x] PRD created and reviewed
- [ ] TRD created and approved ← **NEXT STEP**
- [ ] Tasks decomposed in tasks.md
- [ ] Technology stack validated

### Phase 2: Implementation ⏳

- [ ] Backend API (REQ-001, REQ-002, REQ-003)
- [ ] Frontend UI (REQ-004)
- [ ] Integration testing
- [ ] Security validation

### Phase 3: Deployment ⏳

- [ ] Vercel deployment configured (REQ-005)
- [ ] Environment variables secured
- [ ] Monitoring enabled (NFR-002)
- [ ] Production validation

### Phase 4: Validation ⏳

- [ ] All NFRs verified in production
- [ ] User acceptance testing
- [ ] Performance benchmarking
- [ ] Documentation complete

---

## Troubleshooting & Common Issues

### GPT-4o Integration Issues

```yaml
Symptom: Low extraction accuracy
Agent: deep-debugger
Investigation:
  - Review GPT-4o prompt engineering
  - Test with diverse invoice samples
  - Check confidence_score distribution
  - Analyze common failure patterns
```

### Performance Bottlenecks

```yaml
Symptom: Parse time >20s
Agent: deep-debugger → backend-developer
Investigation:
  - Profile GPT-4o API latency
  - Check file preprocessing time
  - Analyze network overhead
  - Consider parallel processing
```

### Deployment Issues

```yaml
Symptom: Vercel build failures
Agent: devops-engineer
Investigation:
  - Review build logs
  - Validate environment variables
  - Check dependencies and versions
  - Test local build first
```

---

**Last Updated**: 2025-10-20
**Next Review**: After TRD creation
**Maintainer**: James Simmons (james.simmons@fortiumpartners.com)

---

*AI-Augmented Development Process - Invoice Parser Edition*
*Orchestration-First Architecture for AI-Powered Document Processing*
