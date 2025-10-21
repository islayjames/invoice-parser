/**
 * Invoice Parser API Client
 *
 * This module provides a typed interface to the invoice parsing API.
 * It handles file uploads, timeout management, and error handling for invoice parsing requests.
 *
 * @module lib/api/invoiceParser
 */

/**
 * Represents a field value with confidence score from the invoice parser
 */
interface FieldValue {
  value: string
  confidence: number
}

/**
 * Supplier information extracted from the invoice
 */
interface Supplier {
  name?: FieldValue
  address?: FieldValue
  phone?: FieldValue
  email?: FieldValue
  tax_id?: FieldValue
}

/**
 * Customer information extracted from the invoice
 */
interface Customer {
  name?: FieldValue
  address?: FieldValue
  account_id?: FieldValue
}

/**
 * Invoice metadata and financial summary
 */
interface InvoiceDetails {
  number?: FieldValue
  issue_date?: FieldValue
  due_date?: FieldValue
  po_number?: FieldValue
  subtotal?: FieldValue
  tax?: FieldValue
  total?: FieldValue
  currency?: FieldValue
  payment_terms?: FieldValue
}

/**
 * Individual line item from the invoice
 */
interface LineItem {
  description?: FieldValue
  quantity?: FieldValue
  unit_price?: FieldValue
  total?: FieldValue
  sku?: FieldValue
}

/**
 * Processing metadata returned by the API
 */
interface InvoiceMeta {
  processing_time_ms: number
  model_version: string
  warning?: string
}

/**
 * Complete invoice parsing response from the API
 */
export interface InvoiceResponse {
  supplier: Supplier
  customer: Customer
  invoice: InvoiceDetails
  line_items: LineItem[]
  meta: InvoiceMeta
}

/**
 * Error response structure from the API
 */
export interface ErrorResponse {
  code: string
  message: string
  details?: object
}

/**
 * Custom error class for API errors
 */
export class InvoiceParserError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: object
  ) {
    super(message)
    this.name = 'InvoiceParserError'
  }
}

/**
 * Parses an invoice file using the backend API.
 *
 * This function uploads the provided file to the invoice parsing API and returns
 * the structured invoice data. It includes timeout handling (25 seconds) and
 * comprehensive error handling for network issues, timeouts, and API errors.
 *
 * @param file - The invoice file to parse (PDF, image, or text file)
 * @returns Promise resolving to structured invoice data
 * @throws {InvoiceParserError} When parsing fails due to timeout, network issues, or API errors
 *
 * @example
 * ```typescript
 * try {
 *   const invoice = await parseInvoice(file);
 *   console.log('Invoice number:', invoice.invoice.number?.value);
 * } catch (error) {
 *   if (error instanceof InvoiceParserError) {
 *     console.error('Parsing failed:', error.code, error.message);
 *   }
 * }
 * ```
 */
export async function parseInvoice(file: File): Promise<InvoiceResponse> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL

  if (!apiBaseUrl) {
    throw new InvoiceParserError(
      'CONFIG_ERROR',
      'API base URL is not configured. Please set NEXT_PUBLIC_API_BASE_URL environment variable.'
    )
  }

  try {
    // Prepare the form data with the file
    const formData = new FormData()
    formData.append('file', file)

    // Set up abort controller for timeout handling (25 seconds)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 25000)

    // Make the API request
    const response = await fetch(`${apiBaseUrl}/api/parse`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    })

    // Clear the timeout once response is received
    clearTimeout(timeoutId)

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        code: 'API_ERROR',
        message: `Server returned ${response.status}: ${response.statusText}`,
      }))
      throw new InvoiceParserError(
        errorData.code || 'API_ERROR',
        errorData.message,
        errorData.details
      )
    }

    // Parse and return the successful response
    const data: InvoiceResponse = await response.json()
    return data

  } catch (err: any) {
    console.error('[InvoiceParser] Error parsing invoice:', err)

    // Handle timeout errors
    if (err.name === 'AbortError') {
      throw new InvoiceParserError(
        'TIMEOUT',
        'Request timed out after 25 seconds',
        { timeout: '25s' }
      )
    }

    // Re-throw if already an InvoiceParserError
    if (err instanceof InvoiceParserError) {
      throw err
    }

    // Handle API error responses
    if (err.code && err.message) {
      throw new InvoiceParserError(err.code, err.message, err.details)
    }

    // Handle generic network/fetch errors
    throw new InvoiceParserError(
      'NETWORK_ERROR',
      err.message || 'Failed to connect to the API server',
      { originalError: err.toString() }
    )
  }
}
