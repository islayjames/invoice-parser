# UI Specification Document — Invoice Parser Frontend

## 0) Meta

* **UI-SPEC ID:** UI-SPEC-20251020-INVOICE-PARSER
* **Version:** 1.0
* **Status:** Ready for V0 Generation
* **Last Updated:** 2025-10-20
* **PRD Reference:** [PRD-20251020-INVOICE-PARSER v1.1](/home/james/dev/invoice-parser/docs/PRD/PRD-20251020-invoice-parser.md)
* **TRD Reference:** [TRD-20251020-INVOICE-PARSER v1.0](/home/james/dev/invoice-parser/docs/TRD/TRD-20251020-invoice-parser.md)
* **Target Platform:** V0 by Vercel (React + Tailwind CSS + shadcn/ui)
* **Framework:** React 18+ with Next.js (optional) or Vite
* **UI Library:** shadcn/ui components + Tailwind CSS

---

## 1) Executive Summary

### 1.1) Purpose

This UI specification provides detailed, component-level functional specifications and V0-ready prompts for building the Invoice Parser frontend. Each component specification is designed to be fed directly into V0 by Vercel to generate production-ready React components with Tailwind CSS styling.

### 1.2) Design Philosophy

**Desktop-First, Professional Design:**
- Clean, minimal interface focused on functionality
- Table-based invoice layout mimicking traditional invoice formats
- Professional color scheme (blues, grays, white)
- Clear visual hierarchy with proper spacing
- Accessible design following WCAG 2.1 AA standards

**User Experience Principles:**
- **Clarity**: Clear labels, obvious actions, informative feedback
- **Efficiency**: Minimal clicks to complete workflow (upload → view → copy)
- **Feedback**: Loading states, error messages, success indicators
- **Simplicity**: Single-page application, no complex navigation

### 1.3) Technology Stack for V0 Generation

```yaml
Framework: React 18+ (Vite or Next.js)
Styling: Tailwind CSS 3+
UI Components: shadcn/ui library
Icons: Lucide React
State Management: React hooks (useState, useEffect)
HTTP Client: Axios or fetch
Utilities:
  - react-json-view (JSON visualization)
  - native Clipboard API (copy to clipboard)
```

---

## 2) Application Architecture

### 2.1) Page Structure

**Single Page Application (SPA):**

```
┌─────────────────────────────────────────────────────┐
│                   App Header                        │
│  "Invoice Parser Demo"                              │
└─────────────────────────────────────────────────────┘
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │         FileUpload Component                 │    │
│  │  (Drag-drop zone + browse button)           │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │      LoadingSpinner Component                │    │
│  │  (Visible during processing)                 │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │       ErrorDisplay Component                 │    │
│  │  (Visible on error)                          │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │      InvoiceDisplay Component                │    │
│  │  ┌─────────────────────────────────────┐    │    │
│  │  │  Controls (Toggle + Copy Button)    │    │    │
│  │  └─────────────────────────────────────┘    │    │
│  │  ┌─────────────────────────────────────┐    │    │
│  │  │  ConfidenceWarning (if needed)      │    │    │
│  │  └─────────────────────────────────────┘    │    │
│  │  ┌─────────────────────────────────────┐    │    │
│  │  │  FormattedView OR RawView           │    │    │
│  │  │  (Conditional rendering based on    │    │    │
│  │  │   toggle state)                     │    │    │
│  │  └─────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────┘    │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### 2.2) Component Hierarchy

```
App (Root Component)
├── AppHeader
├── FileUpload
├── LoadingSpinner (conditional)
├── ErrorDisplay (conditional)
└── InvoiceDisplay (conditional)
    ├── ControlBar
    │   ├── ViewToggle (Formatted/Raw buttons)
    │   └── CopyButton
    ├── ConfidenceWarning (conditional)
    ├── FormattedView (conditional)
    │   ├── InvoiceHeader
    │   │   ├── SupplierInfo
    │   │   └── InvoiceMetaInfo
    │   ├── CustomerInfo
    │   ├── LineItemsTable
    │   └── PaymentSummary
    └── RawView (conditional)
        └── JSONViewer (react-json-view)
```

### 2.3) State Management

```javascript
// App.jsx state structure
const [state, setState] = useState({
  // File upload state
  selectedFile: null,           // File | null

  // API call state
  loading: false,               // boolean
  error: null,                  // ErrorObject | null

  // Invoice data
  invoiceData: null,            // InvoiceResponse | null

  // View preferences
  viewMode: 'formatted'         // 'formatted' | 'raw'
});
```

---

## 3) Component Specifications for V0

### Component Index

| Component ID | Name | Priority | Dependencies | V0 Prompt Section |
|--------------|------|----------|--------------|-------------------|
| COMP-001 | AppHeader | Medium | None | 3.1 |
| COMP-002 | FileUpload | High | lucide-react | 3.2 |
| COMP-003 | LoadingSpinner | Medium | None | 3.3 |
| COMP-004 | ErrorDisplay | High | lucide-react | 3.4 |
| COMP-005 | InvoiceDisplay | High | COMP-006, COMP-007, COMP-008 | 3.5 |
| COMP-006 | ControlBar | High | lucide-react | 3.6 |
| COMP-007 | ConfidenceWarning | Medium | lucide-react | 3.7 |
| COMP-008 | FormattedView | High | COMP-009 to COMP-013 | 3.8 |
| COMP-009 | InvoiceHeader | High | lucide-react | 3.9 |
| COMP-010 | SupplierInfo | High | None | 3.10 |
| COMP-011 | InvoiceMetaInfo | High | None | 3.11 |
| COMP-012 | CustomerInfo | High | None | 3.12 |
| COMP-013 | LineItemsTable | High | None | 3.13 |
| COMP-014 | PaymentSummary | High | None | 3.14 |
| COMP-015 | RawView | High | react-json-view | 3.15 |

---

## 3.1) COMP-001: AppHeader

### Functional Requirements

**Purpose**: Display application title and branding

**Features**:
- Application title: "Invoice Parser Demo"
- Optional subtitle: "AI-Powered Invoice Data Extraction"
- Clean, professional header with subtle shadow

**Props**: None

**Visual Design**:
- Background: White with subtle bottom border
- Text: Large, bold title (text-2xl or text-3xl)
- Padding: Generous padding (py-6 px-8)
- Position: Sticky top (optional)

### V0 Prompt for COMP-001

```
Create a React component called AppHeader for an invoice parsing application.

Requirements:
- Display the title "Invoice Parser Demo" in large, bold text (text-3xl font-bold)
- Include a subtitle "AI-Powered Invoice Data Extraction" in smaller, muted text (text-sm text-muted-foreground)
- Use a clean white background with a subtle bottom border (border-b)
- Add generous padding (py-6 px-8)
- Center-align the text content
- Use Tailwind CSS for styling
- Make it responsive (stack title and subtitle on mobile if needed)

Design Style:
- Professional and clean
- Use slate/gray color scheme
- Minimal decorative elements
- Focus on clarity and readability

The component should not accept any props and be a simple presentational component.
```

---

## 3.2) COMP-002: FileUpload

### Functional Requirements

**Purpose**: Allow users to upload invoice files via drag-drop or click-to-browse

**Features**:
- Drag-and-drop zone with visual feedback (hover state)
- Click-to-browse file input (hidden input, styled button/zone)
- File type validation (client-side)
- File size validation (≤5MB, client-side)
- File preview after selection (filename, size)
- Clear/remove file button
- Disabled state during processing
- Visual states: default, hover, active (dragging), disabled

**Props**:
```typescript
interface FileUploadProps {
  onFileSelect: (file: File) => void;  // Callback when file selected
  disabled?: boolean;                   // Disable during processing
  acceptedFormats?: string[];           // Default: ['.pdf', '.jpg', '.jpeg', '.png', ...]
  maxSizeMB?: number;                   // Default: 5
}
```

**Client-Side Validation**:
- File types: PDF, JPEG, PNG, TIFF, BMP, WebP, HEIC, HEIF, GIF, TXT, MD
- Max size: 5MB (configurable via prop)
- Display error message if validation fails

**Visual Design**:
- Large, dashed border box (border-dashed border-2)
- Upload icon (Cloud Upload from lucide-react)
- Instructional text: "Drag and drop your invoice here, or click to browse"
- Supported formats text: "Supports PDF, images (JPG, PNG, etc.), and text files up to 5MB"
- Hover state: border color change, slight background tint
- Active drag state: stronger border color, background highlight

### V0 Prompt for COMP-002

```
Create a React component called FileUpload for uploading invoice files with drag-and-drop support.

Requirements:
- Large dashed border box (border-dashed border-2 border-gray-300) that serves as a drop zone
- Display a cloud upload icon from lucide-react (CloudUpload) centered at the top
- Main text: "Drag and drop your invoice here, or click to browse" (text-base font-medium)
- Secondary text: "Supports PDF, images (JPG, PNG, etc.), and text files up to 5MB" (text-sm text-muted-foreground)
- Clicking anywhere in the box should trigger a file input dialog
- Support drag-and-drop file upload with visual feedback:
  - Hover state: border-blue-400 bg-blue-50/50
  - Active drag state: border-blue-600 bg-blue-100
- Show selected file preview after selection:
  - Display filename and file size
  - Show a "Remove" or "Clear" button to deselect
- Client-side validation:
  - Accept only: .pdf, .jpg, .jpeg, .png, .tiff, .tif, .bmp, .webp, .heic, .heif, .gif, .txt, .md
  - Max file size: 5MB
  - Display inline error message if validation fails (text-red-600)
- Disabled state: opacity-50 cursor-not-allowed (when disabled prop is true)

Props:
- onFileSelect: (file: File) => void - Called when a valid file is selected
- disabled?: boolean - Whether the upload is disabled (e.g., during processing)
- acceptedFormats?: string[] - Array of accepted file extensions (default: PDF and image formats)
- maxSizeMB?: number - Maximum file size in MB (default: 5)

Styling:
- Use Tailwind CSS
- Use shadcn/ui Button component for the "Browse" text/action if applicable
- Responsive design: works well on desktop (min-width: 600px)
- Clean, professional look with blue accent colors
- Smooth transitions for hover/active states

State management:
- Track selected file internally
- Track drag-over state for visual feedback
- Display validation errors
```

---

## 3.3) COMP-003: LoadingSpinner

### Functional Requirements

**Purpose**: Display loading indicator during invoice processing

**Features**:
- Animated spinner (rotating circle or dots)
- Loading message: "Processing your invoice..."
- Progress indicator (optional: "This may take up to 20 seconds")
- Centered on screen
- Semi-transparent backdrop (optional)

**Props**:
```typescript
interface LoadingSpinnerProps {
  message?: string;                     // Default: "Processing your invoice..."
  showEstimate?: boolean;               // Show time estimate (default: true)
}
```

**Visual Design**:
- Centered spinner animation
- Text below spinner
- Subtle animation (rotate or pulse)
- Professional, calming colors (blue or gray)

### V0 Prompt for COMP-003

```
Create a React component called LoadingSpinner for displaying a loading state during invoice processing.

Requirements:
- Centered animated spinner using lucide-react's Loader2 icon with animate-spin
- Display message: "Processing your invoice..." (text-lg font-medium)
- Display secondary message: "This may take up to 20 seconds" (text-sm text-muted-foreground)
- Center the entire component vertically and horizontally on the screen
- Use a clean, professional design with blue accent color for the spinner

Props:
- message?: string - Custom loading message (default: "Processing your invoice...")
- showEstimate?: boolean - Whether to show the time estimate (default: true)

Styling:
- Use Tailwind CSS
- Flex layout for centering
- Spinner size: w-12 h-12
- Spacing between spinner and text: mt-4
- Overall container should have min-height to take up appropriate space
- Use text-blue-600 for the spinner color

The component should be visually calming and indicate that processing is ongoing.
```

---

## 3.4) COMP-004: ErrorDisplay

### Functional Requirements

**Purpose**: Display error messages when invoice processing fails

**Features**:
- Error icon (Alert Circle from lucide-react)
- Error code (e.g., "FILE_TOO_LARGE", "CONFIDENCE_TOO_LOW")
- Error message (user-friendly description)
- Error details (collapsible section, optional)
- Retry button (optional, triggers parent re-upload)
- Dismiss button (clear error state)

**Props**:
```typescript
interface ErrorDisplayProps {
  error: {
    code: string;                       // Error code
    message: string;                    // User-friendly message
    details?: Record<string, any>;     // Additional details
  };
  onRetry?: () => void;                 // Retry callback
  onDismiss?: () => void;               // Dismiss callback
}
```

**Error Types to Handle**:
- FILE_TOO_LARGE: "File size exceeds maximum limit of 5MB"
- UNSUPPORTED_FILE_TYPE: "File type not supported. Please upload PDF, image, or text files."
- CONFIDENCE_TOO_LOW: "Unable to extract required fields with sufficient confidence"
- PROCESSING_TIMEOUT: "Invoice processing exceeded maximum time limit"
- SERVICE_UNAVAILABLE: "AI processing service temporarily unavailable"
- UNKNOWN_ERROR: "An unexpected error occurred"

**Visual Design**:
- Red/orange color scheme for alerts
- Alert icon on the left
- Error message prominently displayed
- Details collapsible (chevron icon)
- Action buttons at bottom (Retry, Dismiss)

### V0 Prompt for COMP-004

```
Create a React component called ErrorDisplay for showing error messages from the invoice parsing API.

Requirements:
- Display a prominent error alert using shadcn/ui Alert or Card component
- Show an AlertCircle icon from lucide-react on the left (text-red-600)
- Display error code in bold uppercase (text-xs font-bold text-red-700)
- Display error message prominently (text-base text-red-800)
- If error details exist, show a collapsible section:
  - "Show Details" button with ChevronDown/ChevronUp icon
  - When expanded, display error details as formatted JSON or key-value pairs
- Action buttons at the bottom:
  - "Try Again" button (if onRetry prop provided)
  - "Dismiss" button (if onDismiss prop provided)

Props:
- error: { code: string; message: string; details?: Record<string, any> }
- onRetry?: () => void - Optional callback for retry action
- onDismiss?: () => void - Optional callback for dismiss action

Styling:
- Use Tailwind CSS with red/orange color scheme
- Background: bg-red-50 border-red-200
- Use shadcn/ui Alert component or Card with border-l-4 border-red-500
- Buttons: Primary "Try Again" (blue), Secondary "Dismiss" (gray)
- Smooth expand/collapse animation for details section
- Responsive design

State management:
- Track whether details section is expanded (useState)

The component should clearly communicate what went wrong and provide actionable next steps.
```

---

## 3.5) COMP-005: InvoiceDisplay

### Functional Requirements

**Purpose**: Container component that orchestrates invoice data display

**Features**:
- Manages view mode state (formatted vs raw)
- Renders ControlBar (toggle + copy button)
- Conditionally renders ConfidenceWarning
- Conditionally renders FormattedView or RawView

**Props**:
```typescript
interface InvoiceDisplayProps {
  data: InvoiceResponse;               // Complete invoice data from API
}
```

**Layout**:
```
┌──────────────────────────────────────────┐
│ ControlBar (Toggle + Copy)              │
├──────────────────────────────────────────┤
│ ConfidenceWarning (if warning exists)   │
├──────────────────────────────────────────┤
│                                          │
│ FormattedView (if viewMode=formatted)   │
│        OR                                │
│ RawView (if viewMode=raw)               │
│                                          │
└──────────────────────────────────────────┘
```

### V0 Prompt for COMP-005

```
Create a React component called InvoiceDisplay that acts as a container for displaying parsed invoice data.

Requirements:
- Accept invoice data as a prop (InvoiceResponse object with supplier, customer, invoice, line_items, meta fields)
- Manage view mode state: 'formatted' or 'raw' (useState, default: 'formatted')
- Render child components in this order:
  1. ControlBar component (pass viewMode, setViewMode, invoiceData, handleCopy function)
  2. ConfidenceWarning component (only if data.meta.warning exists)
  3. FormattedView (if viewMode === 'formatted') or RawView (if viewMode === 'raw')
- Implement copy-to-clipboard functionality:
  - Create handleCopy function that copies full JSON (JSON.stringify(data, null, 2)) to clipboard
  - Show success toast/alert after successful copy
  - Handle copy errors gracefully

Props:
- data: InvoiceResponse (TypeScript interface matching API response schema)

Styling:
- Use Tailwind CSS
- Container: bg-white border rounded-lg shadow-sm
- Padding: p-6
- Spacing between sections: space-y-4
- Max width: max-w-5xl mx-auto

State management:
- viewMode: 'formatted' | 'raw'

The component should orchestrate the display logic and pass appropriate data to child components.
```

---

## 3.6) COMP-006: ControlBar

### Functional Requirements

**Purpose**: Provide view toggle and copy-to-clipboard controls

**Features**:
- Toggle buttons: "Formatted View" and "Raw JSON"
- Active state styling for selected view
- Copy to clipboard button (with icon)
- Responsive layout (stack on mobile)

**Props**:
```typescript
interface ControlBarProps {
  viewMode: 'formatted' | 'raw';
  onViewModeChange: (mode: 'formatted' | 'raw') => void;
  onCopy: () => void;
}
```

**Visual Design**:
- Button group for toggle (styled as tabs or toggle buttons)
- Copy button on the right side
- Flex layout with space-between
- Active button has different background/border

### V0 Prompt for COMP-006

```
Create a React component called ControlBar with view toggle and copy button controls.

Requirements:
- Flex layout with space-between alignment
- Left side: Toggle button group with two buttons:
  - "Formatted View" button
  - "Raw JSON" button
  - Active button: bg-blue-600 text-white
  - Inactive button: bg-white text-gray-700 border hover:bg-gray-50
  - Use shadcn/ui Button component or custom styled buttons
- Right side: Copy to clipboard button
  - Icon: Copy from lucide-react
  - Text: "Copy JSON"
  - Variant: outline or secondary
  - onClick triggers onCopy callback

Props:
- viewMode: 'formatted' | 'raw' - Current view mode
- onViewModeChange: (mode: 'formatted' | 'raw') => void - Callback when view changes
- onCopy: () => void - Callback for copy action

Styling:
- Use Tailwind CSS
- Responsive: On mobile (sm), stack buttons vertically or reduce padding
- Button group should look cohesive (connected or closely spaced)
- Smooth transitions for hover/active states
- Padding: py-3 px-4
- Border bottom: border-b border-gray-200

The component should provide clear, accessible controls for switching views and copying data.
```

---

## 3.7) COMP-007: ConfidenceWarning

### Functional Requirements

**Purpose**: Alert users when field confidence scores are low

**Features**:
- Warning icon (Alert Triangle from lucide-react)
- Warning message from API (data.meta.warning)
- Dismissible (optional)
- Yellow/orange color scheme

**Props**:
```typescript
interface ConfidenceWarningProps {
  message: string;                      // Warning message from API
  onDismiss?: () => void;               // Optional dismiss callback
}
```

**Visual Design**:
- Yellow/orange alert background
- Warning icon on left
- Message text
- Optional close button

### V0 Prompt for COMP-007

```
Create a React component called ConfidenceWarning for displaying low confidence alerts.

Requirements:
- Use shadcn/ui Alert component with warning variant
- Display AlertTriangle icon from lucide-react (text-yellow-600)
- Show warning message prominently (text-sm text-yellow-800)
- If onDismiss prop provided, show a close button (X icon) on the right
- Yellow/amber color scheme

Props:
- message: string - Warning message to display
- onDismiss?: () => void - Optional callback for dismiss action

Styling:
- Background: bg-yellow-50 border-yellow-300
- Icon color: text-yellow-600
- Text color: text-yellow-800
- Border: border-l-4 border-yellow-500
- Padding: p-4
- Rounded corners: rounded-md
- Flex layout: icon on left, message in center, close button on right (if applicable)

The component should clearly indicate that some data may be uncertain without being alarming.
```

---

## 3.8) COMP-008: FormattedView

### Functional Requirements

**Purpose**: Display invoice data in traditional invoice format (mimics printed invoice)

**Features**:
- Traditional invoice layout with header, body, footer
- Renders InvoiceHeader (supplier + invoice meta info)
- Renders CustomerInfo ("Bill To" section)
- Renders LineItemsTable (if line items exist)
- Renders PaymentSummary (subtotal, tax, total)

**Props**:
```typescript
interface FormattedViewProps {
  data: InvoiceResponse;               // Complete invoice data
}
```

**Layout**:
```
┌────────────────────────────────────────────────┐
│ InvoiceHeader                                  │
│ ┌──────────────────┐  ┌──────────────────┐    │
│ │ SupplierInfo     │  │ InvoiceMetaInfo  │    │
│ └──────────────────┘  └──────────────────┘    │
├────────────────────────────────────────────────┤
│ CustomerInfo (Bill To)                         │
├────────────────────────────────────────────────┤
│ LineItemsTable                                 │
│ ┌────────────────────────────────────────────┐ │
│ │ Description | Qty | Price | Total         │ │
│ │ ...rows...                                 │ │
│ └────────────────────────────────────────────┘ │
├────────────────────────────────────────────────┤
│ PaymentSummary                                 │
│                          Subtotal: $XXX.XX     │
│                          Tax:      $XXX.XX     │
│                          Total:    $XXX.XX USD │
└────────────────────────────────────────────────┘
```

### V0 Prompt for COMP-008

```
Create a React component called FormattedView that displays invoice data in a traditional invoice layout.

Requirements:
- Render child components in this structure:
  1. InvoiceHeader component (pass supplier and invoice metadata)
  2. CustomerInfo component (pass customer data)
  3. LineItemsTable component (pass line_items array, only if not empty)
  4. PaymentSummary component (pass invoice totals)
- Use a clean, professional invoice design that mimics traditional printed invoices
- White background with subtle borders between sections

Props:
- data: InvoiceResponse (object with supplier, customer, invoice, line_items, meta)

Styling:
- Use Tailwind CSS
- Container: bg-white border rounded-lg p-8
- Section spacing: space-y-6
- Professional typography (use different font sizes for hierarchy)
- Subtle dividers between sections (border-t border-gray-200)

Layout:
- Desktop-optimized (min-width: 800px ideal)
- Clean spacing and alignment
- Reference traditional invoice layouts (header with logo/info, bill to, items table, totals)

The component should decompose the invoice data and pass it to specialized child components for rendering.
```

---

## 3.9) COMP-009: InvoiceHeader

### Functional Requirements

**Purpose**: Display invoice header with supplier info and invoice metadata side-by-side

**Features**:
- Two-column layout (supplier on left, invoice meta on right)
- Renders SupplierInfo and InvoiceMetaInfo subcomponents
- Responsive (stack on small screens)

**Props**:
```typescript
interface InvoiceHeaderProps {
  supplier: SupplierInfo;              // Supplier data
  invoice: InvoiceSummary;             // Invoice metadata
}
```

### V0 Prompt for COMP-009

```
Create a React component called InvoiceHeader that displays supplier information and invoice metadata side-by-side.

Requirements:
- Two-column grid layout (grid grid-cols-2 gap-8)
- Left column: Render SupplierInfo component (pass supplier prop)
- Right column: Render InvoiceMetaInfo component (pass invoice prop)
- Responsive: Stack vertically on small screens (grid-cols-1 on mobile)

Props:
- supplier: { name, address, phone, email, tax_id } (each field has { value, confidence })
- invoice: { number, issue_date, due_date, po_number, ... } (each field has { value, confidence })

Styling:
- Use Tailwind CSS
- Padding bottom: pb-6
- Border bottom: border-b border-gray-200
- Gap between columns: gap-8
- Responsive breakpoint: sm:grid-cols-2

The component should create a professional invoice header layout.
```

---

## 3.10) COMP-010: SupplierInfo

### Functional Requirements

**Purpose**: Display supplier/vendor information

**Features**:
- Company name (large, bold)
- Address (multi-line)
- Phone number
- Email
- Tax ID
- Show only fields that have values

**Props**:
```typescript
interface SupplierInfoProps {
  supplier: {
    name: { value: string; confidence: number };
    address?: { value: string; confidence: number };
    phone?: { value: string; confidence: number };
    email?: { value: string; confidence: number };
    tax_id?: { value: string; confidence: number };
  };
}
```

**Visual Design**:
- Name: text-2xl font-bold
- Other fields: text-sm
- Muted color for labels

### V0 Prompt for COMP-010

```
Create a React component called SupplierInfo that displays supplier/vendor information.

Requirements:
- Display supplier name in large, bold text (text-2xl font-bold text-gray-900)
- Display address, phone, email, tax_id in smaller text (text-sm text-gray-600)
- Only render fields that have values (check if field?.value exists)
- Format:
  - Name (bold, large)
  - Address (plain text, may be multi-line)
  - Phone (prefix with "Phone: ")
  - Email (prefix with "Email: ")
  - Tax ID (prefix with "Tax ID: ")

Props:
- supplier: object with name, address, phone, email, tax_id fields
  - Each field is an object: { value: string, confidence: number }
  - Fields except name are optional

Styling:
- Use Tailwind CSS
- Stack fields vertically (flex flex-col space-y-1)
- Name: text-2xl font-bold
- Other fields: text-sm text-gray-600
- Line height: leading-relaxed for readability

The component should display supplier information cleanly and professionally.
```

---

## 3.11) COMP-011: InvoiceMetaInfo

### Functional Requirements

**Purpose**: Display invoice metadata (number, dates, PO)

**Features**:
- "INVOICE" heading (large, uppercase)
- Invoice number
- Issue date
- Due date
- PO number (if exists)

**Props**:
```typescript
interface InvoiceMetaInfoProps {
  invoice: {
    number: { value: string; confidence: number };
    issue_date: { value: string; confidence: number };
    due_date: { value: string; confidence: number };
    po_number?: { value: string; confidence: number };
  };
}
```

**Visual Design**:
- Right-aligned text
- "INVOICE" heading: text-3xl font-bold uppercase
- Labels in gray, values in black

### V0 Prompt for COMP-011

```
Create a React component called InvoiceMetaInfo that displays invoice metadata.

Requirements:
- Display heading "INVOICE" (text-3xl font-bold uppercase text-gray-900)
- Display invoice number, issue date, due date, and PO number (if exists)
- Right-align all text (text-right)
- Format each line as "Label: Value"
  - Labels in gray (text-gray-600)
  - Values in bold black (font-semibold text-gray-900)
- Format dates as readable strings (e.g., "Jan 15, 2025" from "2025-01-15")

Props:
- invoice: object with number, issue_date, due_date, po_number fields
  - Each field is an object: { value: string, confidence: number }
  - po_number is optional

Styling:
- Use Tailwind CSS
- Right-aligned: text-right
- Stack fields vertically: space-y-1
- Heading: text-3xl font-bold mb-4
- Labels: text-sm text-gray-600
- Values: text-sm font-semibold text-gray-900

Format dates:
- Convert YYYY-MM-DD to readable format (e.g., "January 15, 2025")

The component should display invoice metadata clearly with right alignment.
```

---

## 3.12) COMP-012: CustomerInfo

### Functional Requirements

**Purpose**: Display customer "Bill To" information

**Features**:
- "Bill To:" heading
- Customer name (bold)
- Address (multi-line)
- Account ID (if exists)

**Props**:
```typescript
interface CustomerInfoProps {
  customer: {
    name: { value: string; confidence: number };
    address?: { value: string; confidence: number };
    account_id?: { value: string; confidence: number };
  };
}
```

**Visual Design**:
- Heading: "Bill To:" (text-sm font-semibold text-gray-700)
- Customer name: text-lg font-bold
- Other fields: text-sm

### V0 Prompt for COMP-012

```
Create a React component called CustomerInfo that displays customer "Bill To" information.

Requirements:
- Display heading "Bill To:" (text-sm font-semibold text-gray-700 uppercase)
- Display customer name in bold (text-lg font-bold text-gray-900)
- Display address in regular text (text-sm text-gray-600)
- Display account ID with label "Account: " (text-sm text-gray-600)
- Only render fields that have values

Props:
- customer: object with name, address, account_id fields
  - Each field is an object: { value: string, confidence: number }
  - address and account_id are optional

Styling:
- Use Tailwind CSS
- Container: bg-gray-50 border-l-4 border-blue-500 p-4 rounded-r
- Stack fields vertically: space-y-1
- Heading: text-sm font-semibold text-gray-700 uppercase mb-2
- Customer name: text-lg font-bold
- Other fields: text-sm text-gray-600

The component should create a distinct "Bill To" section that stands out visually.
```

---

## 3.13) COMP-013: LineItemsTable

### Functional Requirements

**Purpose**: Display invoice line items in a table format

**Features**:
- Table with columns: Description, Quantity, Unit Price, Total
- Optional columns (show if data exists): SKU, Discount, Tax Rate
- Responsive table design
- Alternating row colors for readability
- Display up to 50 line items

**Props**:
```typescript
interface LineItemsTableProps {
  lineItems: Array<{
    sku?: { value: string; confidence: number };
    description: { value: string; confidence: number };
    quantity: { value: number; confidence: number };
    unit_price: { value: number; confidence: number };
    discount?: { value: number; confidence: number };
    tax_rate?: { value: number; confidence: number };
    total: { value: number; confidence: number };
  }>;
  currency?: string;                   // Default: "USD"
}
```

**Visual Design**:
- Table header: bg-gray-100 font-semibold
- Alternating row colors: even rows bg-gray-50
- Number alignment: right-align for numbers, left-align for descriptions
- Currency formatting: $X,XXX.XX

### V0 Prompt for COMP-013

```
Create a React component called LineItemsTable that displays invoice line items in a table.

Requirements:
- Render a table with columns: Description, Quantity, Unit Price, Total
- Optionally show SKU column (only if any line item has SKU)
- Table header: bg-gray-100 font-semibold text-left
- Alternating row colors: odd rows white, even rows bg-gray-50
- Right-align numeric columns (Quantity, Unit Price, Total)
- Left-align text columns (SKU, Description)
- Format currency values: $1,234.56
- Format quantity as integer or decimal (e.g., "10" or "2.5")
- Display "No line items" message if lineItems array is empty

Props:
- lineItems: array of line item objects
  - Each item has: sku?, description, quantity, unit_price, discount?, tax_rate?, total
  - Each field is an object: { value: string | number, confidence: number }
- currency?: string (default: "USD")

Styling:
- Use Tailwind CSS
- Table: w-full border-collapse
- Borders: border border-gray-200
- Header: bg-gray-100 text-sm font-semibold text-gray-700
- Cells: p-3
- Hover: hover:bg-gray-100 for rows
- Responsive: on mobile, consider stacking or horizontal scroll

The component should create a professional, readable line items table.
```

---

## 3.14) COMP-014: PaymentSummary

### Functional Requirements

**Purpose**: Display invoice payment summary (subtotal, tax, total)

**Features**:
- Right-aligned summary section
- Display subtotal (if exists)
- Display tax (if exists)
- Display total (bold, larger)
- Display payment terms (if exists)
- Currency display

**Props**:
```typescript
interface PaymentSummaryProps {
  invoice: {
    subtotal?: { value: number; confidence: number };
    tax?: { value: number; confidence: number };
    total: { value: number; confidence: number };
    currency: { value: string; confidence: number };
    payment_terms?: { value: string; confidence: number };
  };
}
```

**Visual Design**:
- Right-aligned totals section
- Subtotal and tax: regular weight
- Total: text-xl font-bold
- Payment terms: italicized, smaller text below totals

### V0 Prompt for COMP-014

```
Create a React component called PaymentSummary that displays invoice payment totals.

Requirements:
- Right-aligned summary section (ml-auto max-w-sm)
- Display rows for:
  - Subtotal (if exists): "Subtotal: $XXX.XX"
  - Tax (if exists): "Tax: $XXX.XX"
  - Total (always): "Total: $XXX.XX [CURRENCY]" (bold, larger)
- Display payment terms below totals (if exists): "Payment Terms: Net 30" (italic, smaller)
- Right-align all text
- Format currency with commas and 2 decimal places

Props:
- invoice: object with subtotal?, tax?, total, currency, payment_terms? fields
  - Each field is an object: { value: number | string, confidence: number }

Styling:
- Use Tailwind CSS
- Container: bg-gray-50 border-t border-gray-200 pt-4 px-6 pb-6
- Right-align: text-right
- Subtotal/Tax rows: text-base text-gray-700
- Total row: text-xl font-bold text-gray-900 border-t border-gray-300 pt-2 mt-2
- Payment terms: text-sm italic text-gray-600 mt-3
- Spacing: space-y-1 for summary rows

The component should create a clear, professional payment summary section.
```

---

## 3.15) COMP-015: RawView

### Functional Requirements

**Purpose**: Display complete invoice JSON response in a formatted, collapsible viewer

**Features**:
- Pretty-printed JSON with syntax highlighting
- Collapsible nodes for nested objects/arrays
- Search functionality (if using react-json-view)
- Copy individual values (if using react-json-view)
- Monospace font

**Props**:
```typescript
interface RawViewProps {
  data: InvoiceResponse;               // Complete invoice data
}
```

**Visual Design**:
- Monospace font
- Syntax highlighting (keys, strings, numbers, booleans)
- Indentation for nested structures
- Dark theme or light theme option

**Library**: react-json-view or custom JSON renderer

### V0 Prompt for COMP-015

```
Create a React component called RawView that displays complete invoice JSON data.

Requirements:
- Use react-json-view library to render the JSON data
- Configure react-json-view options:
  - theme: "rjv-default" or "monokai" (clean, readable theme)
  - collapsed: false (expand all by default, but allow collapsing)
  - displayDataTypes: false (hide data type labels for cleaner view)
  - displayObjectSize: true (show object/array sizes)
  - enableClipboard: true (allow copying values)
  - name: "invoice" (root object name)
  - indentWidth: 2 (2-space indentation)
  - iconStyle: "triangle" (use triangle icons for collapsing)
- Fallback: if react-json-view unavailable, render JSON.stringify(data, null, 2) in a <pre> tag

Props:
- data: InvoiceResponse (complete invoice object)

Styling:
- Container: bg-gray-900 text-gray-100 p-6 rounded-lg (dark theme)
- OR Container: bg-white border border-gray-200 p-6 rounded-lg (light theme)
- Monospace font: font-mono text-sm
- Overflow: overflow-auto max-h-[600px] (scrollable if content is tall)

Installation note:
- Require: npm install react-json-view

The component should provide a developer-friendly view of the complete API response.
```

---

## 4) Complete App Integration

### 4.1) App.jsx Structure

```javascript
// App.jsx - Main application component

import { useState } from 'react';
import AppHeader from './components/AppHeader';
import FileUpload from './components/FileUpload';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorDisplay from './components/ErrorDisplay';
import InvoiceDisplay from './components/InvoiceDisplay';
import { parseInvoice } from './services/api';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [invoiceData, setInvoiceData] = useState(null);

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setLoading(true);
    setError(null);
    setInvoiceData(null);

    try {
      const data = await parseInvoice(file);
      setInvoiceData(data);
    } catch (err) {
      setError(err.response?.data?.error || {
        code: 'UNKNOWN_ERROR',
        message: err.message
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setSelectedFile(null);
  };

  const handleDismissError = () => {
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <FileUpload
          onFileSelect={handleFileSelect}
          disabled={loading}
        />

        {loading && <LoadingSpinner />}

        {error && (
          <ErrorDisplay
            error={error}
            onRetry={handleRetry}
            onDismiss={handleDismissError}
          />
        )}

        {invoiceData && <InvoiceDisplay data={invoiceData} />}
      </main>
    </div>
  );
}

export default App;
```

### 4.2) API Service (api.js)

```javascript
// services/api.js

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 25000, // 25s (slightly more than backend 20s limit)
});

export async function parseInvoice(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/parse', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}
```

### V0 Prompt for Complete App

```
Create a complete React application called "Invoice Parser Demo" with the following structure:

Requirements:
- Single-page application with these main sections:
  1. AppHeader - Application title and branding
  2. FileUpload - Drag-drop file upload zone
  3. LoadingSpinner - Shows during processing (conditional)
  4. ErrorDisplay - Shows errors (conditional)
  5. InvoiceDisplay - Shows parsed invoice (conditional)

State management:
- selectedFile: File | null
- loading: boolean
- error: { code: string, message: string, details?: object } | null
- invoiceData: InvoiceResponse | null

Workflow:
1. User uploads file via FileUpload component
2. Show LoadingSpinner while processing
3. On success: Display InvoiceDisplay with parsed data
4. On error: Display ErrorDisplay with error details
5. User can retry (clears error, resets to upload state)

API Integration:
- POST /api/parse endpoint
- FormData with 'file' field
- Timeout: 25 seconds
- Error handling for network failures, timeouts, API errors

Styling:
- Use Tailwind CSS
- Clean, professional design
- Desktop-focused (min-width: 1024px optimal)
- Color scheme: Blue accents, gray backgrounds, white containers
- Responsive containers with max-width constraints

Layout:
- Background: bg-gray-50
- Main container: container mx-auto px-4 py-8 max-w-6xl
- Spacing: Generous spacing between sections (space-y-8)

Environment Variables:
- VITE_API_BASE_URL - Backend API URL (default: http://localhost:8000)

Dependencies:
- React 18+
- Tailwind CSS
- Axios
- Lucide React (icons)
- react-json-view (for JSON viewer)
- shadcn/ui components (optional but recommended)

The application should provide a clean, professional interface for uploading invoices and viewing parsed results.
```

---

## 5) Design System & Styling Guidelines

### 5.1) Color Palette

```css
/* Primary Colors */
--primary: #2563eb;         /* Blue 600 */
--primary-hover: #1d4ed8;   /* Blue 700 */
--primary-light: #dbeafe;   /* Blue 100 */

/* Neutral Colors */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-900: #111827;

/* Semantic Colors */
--success: #10b981;         /* Green 500 */
--warning: #f59e0b;         /* Amber 500 */
--error: #ef4444;           /* Red 500 */
--error-bg: #fef2f2;        /* Red 50 */
--warning-bg: #fffbeb;      /* Amber 50 */
```

### 5.2) Typography

```css
/* Font Families */
--font-sans: Inter, system-ui, sans-serif;
--font-mono: 'JetBrains Mono', 'Courier New', monospace;

/* Font Sizes */
--text-xs: 0.75rem;         /* 12px */
--text-sm: 0.875rem;        /* 14px */
--text-base: 1rem;          /* 16px */
--text-lg: 1.125rem;        /* 18px */
--text-xl: 1.25rem;         /* 20px */
--text-2xl: 1.5rem;         /* 24px */
--text-3xl: 1.875rem;       /* 30px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 5.3) Spacing

```css
/* Spacing Scale (Tailwind default) */
--spacing-1: 0.25rem;       /* 4px */
--spacing-2: 0.5rem;        /* 8px */
--spacing-3: 0.75rem;       /* 12px */
--spacing-4: 1rem;          /* 16px */
--spacing-6: 1.5rem;        /* 24px */
--spacing-8: 2rem;          /* 32px */
--spacing-12: 3rem;         /* 48px */
```

### 5.4) Component Styling Conventions

**Containers:**
- Background: `bg-white`
- Border: `border border-gray-200`
- Radius: `rounded-lg` (8px)
- Shadow: `shadow-sm` (subtle)
- Padding: `p-6` or `p-8` for main containers

**Buttons:**
- Primary: `bg-blue-600 hover:bg-blue-700 text-white`
- Secondary: `bg-white hover:bg-gray-50 text-gray-700 border border-gray-300`
- Padding: `px-4 py-2`
- Radius: `rounded-md`
- Transition: `transition-colors duration-150`

**Tables:**
- Header: `bg-gray-100 font-semibold text-gray-700`
- Row hover: `hover:bg-gray-50`
- Borders: `border border-gray-200`
- Cell padding: `p-3`

**Forms:**
- Input: `border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500`
- Label: `text-sm font-medium text-gray-700 mb-1`

---

## 6) Accessibility Requirements

### 6.1) WCAG 2.1 AA Compliance

**Color Contrast:**
- Text on background: minimum 4.5:1 ratio
- Large text: minimum 3:1 ratio
- Interactive elements: clear focus indicators

**Keyboard Navigation:**
- All interactive elements must be keyboard accessible
- Tab order should follow visual flow
- Focus indicators visible and clear

**Screen Reader Support:**
- Semantic HTML elements (header, main, nav, section)
- ARIA labels for icon-only buttons
- Alt text for images (if any)
- Form labels associated with inputs

**Responsive Text:**
- Text resizable up to 200% without loss of functionality
- No horizontal scrolling at 320px width

### 6.2) Accessibility Checklist

- [ ] All buttons have descriptive labels or aria-label
- [ ] File input has associated label
- [ ] Error messages announced to screen readers (aria-live="polite")
- [ ] Loading states announced to screen readers
- [ ] Table headers properly marked with <th> and scope
- [ ] Color is not the only means of conveying information
- [ ] Focus indicators visible on all interactive elements
- [ ] Sufficient color contrast for all text

---

## 7) V0 Generation Workflow

### 7.1) Component Generation Order

**Phase 1: Foundational Components (No dependencies)**
1. COMP-001: AppHeader
2. COMP-003: LoadingSpinner
3. COMP-010: SupplierInfo
4. COMP-011: InvoiceMetaInfo
5. COMP-012: CustomerInfo
6. COMP-013: LineItemsTable
7. COMP-014: PaymentSummary

**Phase 2: Container Components (Depend on Phase 1)**
1. COMP-009: InvoiceHeader (uses SupplierInfo, InvoiceMetaInfo)
2. COMP-008: FormattedView (uses InvoiceHeader, CustomerInfo, LineItemsTable, PaymentSummary)
3. COMP-015: RawView (needs react-json-view)

**Phase 3: Control & Alert Components**
1. COMP-006: ControlBar
2. COMP-007: ConfidenceWarning
3. COMP-004: ErrorDisplay

**Phase 4: Interactive Components**
1. COMP-002: FileUpload
2. COMP-005: InvoiceDisplay (uses ControlBar, ConfidenceWarning, FormattedView, RawView)

**Phase 5: Integration**
1. Complete App.jsx integration
2. API service setup (api.js)

### 7.2) Testing After Each Component

**For each generated component:**
1. Review generated code for:
   - Correct prop types
   - Proper conditional rendering
   - Accessibility attributes
   - Tailwind CSS class usage
2. Test with sample data:
   - Provide mock props matching expected data structure
   - Test with missing optional fields
   - Test edge cases (empty arrays, null values)
3. Refine prompt if needed and regenerate

### 7.3) V0 Best Practices

**Prompt Writing Tips:**
- Be specific about layout (grid, flex, positioning)
- Specify exact Tailwind CSS classes where possible
- Include prop types with TypeScript interface notation
- Mention shadcn/ui components when applicable
- Describe visual hierarchy and spacing
- Include responsive behavior requirements
- Specify icon library (lucide-react)

**Iteration Strategy:**
- Start with simple version, iterate to add complexity
- Use V0's inline editing (Cmd+K) for refinements
- Generate variants and compare
- Combine best features from multiple generations

---

## 8) Sample Data for Testing

### 8.1) Mock Invoice Response

```json
{
  "supplier": {
    "name": { "value": "Acme Corporation", "confidence": 0.98 },
    "address": { "value": "123 Main Street, Suite 100, New York, NY 10001", "confidence": 0.95 },
    "phone": { "value": "+1-555-123-4567", "confidence": 0.92 },
    "email": { "value": "billing@acmecorp.com", "confidence": 0.96 },
    "tax_id": { "value": "12-3456789", "confidence": 0.94 }
  },
  "customer": {
    "name": { "value": "Client Company Inc", "confidence": 0.97 },
    "address": { "value": "456 Oak Avenue, Los Angeles, CA 90001", "confidence": 0.93 },
    "account_id": { "value": "CUST-2025-001", "confidence": 0.89 }
  },
  "invoice": {
    "number": { "value": "INV-2025-001", "confidence": 0.99 },
    "issue_date": { "value": "2025-01-15", "confidence": 0.98 },
    "due_date": { "value": "2025-02-15", "confidence": 0.98 },
    "currency": { "value": "USD", "confidence": 0.85 },
    "subtotal": { "value": 10000.00, "confidence": 0.96 },
    "tax": { "value": 800.00, "confidence": 0.94 },
    "total": { "value": 10800.00, "confidence": 0.99 },
    "payment_terms": { "value": "Net 30", "confidence": 0.91 },
    "po_number": { "value": "PO-2025-100", "confidence": 0.88 }
  },
  "line_items": [
    {
      "sku": { "value": "PROD-001", "confidence": 0.92 },
      "description": { "value": "Professional Services - Q1 2025", "confidence": 0.95 },
      "quantity": { "value": 100, "confidence": 0.97 },
      "unit_price": { "value": 100.00, "confidence": 0.96 },
      "discount": { "value": 0.00, "confidence": 0.90 },
      "tax_rate": { "value": 0.08, "confidence": 0.88 },
      "total": { "value": 10000.00, "confidence": 0.97 }
    }
  ],
  "meta": {
    "source_file_name": "invoice-sample-001.pdf",
    "source_format": "pdf",
    "model_version": "gpt-4o-2024-05-13",
    "extraction_time": "2025-01-20T14:32:10Z",
    "processing_time_ms": 8734,
    "overall_confidence": 0.88,
    "warning": null
  }
}
```

### 8.2) Mock Error Response

```json
{
  "code": "CONFIDENCE_TOO_LOW",
  "message": "Unable to extract required fields with sufficient confidence",
  "details": {
    "failed_fields": ["supplier.name", "invoice.total"],
    "confidence_scores": {
      "supplier.name": 0.42,
      "invoice.total": 0.38
    },
    "minimum_required": 0.50
  }
}
```

### 8.3) Mock Invoice with Warning

```json
{
  "supplier": {
    "name": { "value": "ABC Services Ltd", "confidence": 0.72 }
  },
  "customer": {
    "name": { "value": "XYZ Corp", "confidence": 0.68 }
  },
  "invoice": {
    "number": { "value": "INV-001", "confidence": 0.55 },
    "issue_date": { "value": "2025-01-10", "confidence": 0.82 },
    "due_date": { "value": "2025-02-10", "confidence": 0.78 },
    "currency": { "value": "USD", "confidence": 0.60 },
    "total": { "value": 5000.00, "confidence": 0.65 }
  },
  "line_items": [],
  "meta": {
    "source_file_name": "low-quality-scan.pdf",
    "source_format": "pdf",
    "model_version": "gpt-4o-2024-05-13",
    "extraction_time": "2025-01-20T15:00:00Z",
    "processing_time_ms": 12450,
    "overall_confidence": 0.55,
    "warning": "Some fields have confidence scores between 50-90%. Please review: invoice.number, invoice.total, currency"
  }
}
```

---

## 9) Deployment Considerations

### 9.1) Environment Variables

```bash
# .env.example (for Vite)
VITE_API_BASE_URL=http://localhost:8000

# Production (Vercel)
VITE_API_BASE_URL=https://invoice-parser-backend.railway.app
```

### 9.2) Build Configuration

**Vite (vite.config.js):**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Vercel (vercel.json):**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_BASE_URL": "@api-base-url"
  }
}
```

---

## 10) Quick Reference: All V0 Prompts

**Component Generation Checklist:**

- [ ] COMP-001: AppHeader (Section 3.1)
- [ ] COMP-002: FileUpload (Section 3.2)
- [ ] COMP-003: LoadingSpinner (Section 3.3)
- [ ] COMP-004: ErrorDisplay (Section 3.4)
- [ ] COMP-005: InvoiceDisplay (Section 3.5)
- [ ] COMP-006: ControlBar (Section 3.6)
- [ ] COMP-007: ConfidenceWarning (Section 3.7)
- [ ] COMP-008: FormattedView (Section 3.8)
- [ ] COMP-009: InvoiceHeader (Section 3.9)
- [ ] COMP-010: SupplierInfo (Section 3.10)
- [ ] COMP-011: InvoiceMetaInfo (Section 3.11)
- [ ] COMP-012: CustomerInfo (Section 3.12)
- [ ] COMP-013: LineItemsTable (Section 3.13)
- [ ] COMP-014: PaymentSummary (Section 3.14)
- [ ] COMP-015: RawView (Section 3.15)
- [ ] Complete App Integration (Section 4.2)

**Each prompt is self-contained and includes:**
- Functional requirements
- Props interface
- Styling guidelines
- Tailwind CSS classes
- Accessibility considerations
- Sample data references

---

## 11) Appendix: TypeScript Interfaces

### 11.1) Complete Type Definitions

```typescript
// types/invoice.ts

export interface FieldValue<T = string | number> {
  value: T;
  confidence: number;
}

export interface SupplierInfo {
  name: FieldValue<string>;
  address?: FieldValue<string>;
  phone?: FieldValue<string>;
  email?: FieldValue<string>;
  tax_id?: FieldValue<string>;
}

export interface CustomerInfo {
  name: FieldValue<string>;
  address?: FieldValue<string>;
  account_id?: FieldValue<string>;
}

export interface InvoiceSummary {
  number: FieldValue<string>;
  issue_date: FieldValue<string>;
  due_date: FieldValue<string>;
  currency: FieldValue<string>;
  subtotal?: FieldValue<number>;
  tax?: FieldValue<number>;
  total: FieldValue<number>;
  payment_terms?: FieldValue<string>;
  po_number?: FieldValue<string>;
}

export interface LineItem {
  sku?: FieldValue<string>;
  description: FieldValue<string>;
  quantity: FieldValue<number>;
  unit_price: FieldValue<number>;
  discount?: FieldValue<number>;
  tax_rate?: FieldValue<number>;
  total: FieldValue<number>;
}

export interface InvoiceMetadata {
  source_file_name: string;
  source_format: 'pdf' | 'image' | 'text';
  model_version: string;
  extraction_time: string;
  processing_time_ms: number;
  overall_confidence: number;
  warning: string | null;
}

export interface InvoiceResponse {
  supplier: SupplierInfo;
  customer: CustomerInfo;
  invoice: InvoiceSummary;
  line_items: LineItem[];
  meta: InvoiceMetadata;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: Record<string, any>;
}
```

---

## 12) Changelog

| Version | Date       | Change                                      | Author        |
| ------- | ---------- | ------------------------------------------- | ------------- |
| 1.0     | 2025-10-20 | Initial UI specification with V0 prompts    | James Simmons |

---

**Ready for V0 Generation** ✅

This UI specification provides comprehensive, component-level documentation with production-ready V0 prompts. Each component can be generated independently by copying the corresponding prompt into V0 by Vercel.

**Next Steps**:
1. Review UI specification with stakeholders
2. Begin Phase 1 component generation in V0
3. Test each component with mock data
4. Integrate components into complete application
5. Deploy to Vercel for demo

---

*Invoice Parser UI Specification - V0 Generation Guide*
*Designed for rapid prototyping with AI-powered component generation*
