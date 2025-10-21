"use client"

import { useState } from "react"
import { AppHeader } from "@/components/app-header"
import { FileUpload } from "@/components/file-upload"
import { LoadingSpinner } from "@/components/loading-spinner"
import { ErrorDisplay } from "@/components/error-display"
import { InvoiceDisplay } from "@/components/invoice-display"
import { parseInvoice, InvoiceParserError } from "@/lib/api/invoiceParser"
import type { InvoiceResponse, ErrorResponse } from "@/lib/api/invoiceParser"

const MOCK_INVOICE_DATA: InvoiceResponse = {
  supplier: {
    name: { value: "Acme Corporation", confidence: 0.98 },
    address: { value: "123 Business Park\nSan Francisco, CA 94105", confidence: 0.95 },
    phone: { value: "+1 (555) 123-4567", confidence: 0.92 },
    email: { value: "billing@acmecorp.com", confidence: 0.96 },
    tax_id: { value: "12-3456789", confidence: 0.94 },
  },
  customer: {
    name: { value: "Tech Solutions Inc.", confidence: 0.97 },
    address: { value: "456 Innovation Drive\nAustin, TX 78701", confidence: 0.93 },
    account_id: { value: "CUST-2024-001", confidence: 0.91 },
  },
  invoice: {
    number: { value: "INV-2024-0042", confidence: 0.99 },
    issue_date: { value: "2024-01-15", confidence: 0.98 },
    due_date: { value: "2024-02-14", confidence: 0.97 },
    po_number: { value: "PO-2024-789", confidence: 0.89 },
    subtotal: { value: "8500.00", confidence: 0.96 },
    tax: { value: "765.00", confidence: 0.95 },
    total: { value: "9265.00", confidence: 0.98 },
    currency: { value: "USD", confidence: 0.99 },
    payment_terms: { value: "Net 30", confidence: 0.94 },
  },
  line_items: [
    {
      description: { value: "Professional Services - Q1 2024", confidence: 0.96 },
      quantity: { value: "40", confidence: 0.98 },
      unit_price: { value: "150.00", confidence: 0.97 },
      total: { value: "6000.00", confidence: 0.98 },
      sku: { value: "SRV-001", confidence: 0.92 },
    },
    {
      description: { value: "Software License - Annual", confidence: 0.95 },
      quantity: { value: "5", confidence: 0.99 },
      unit_price: { value: "300.00", confidence: 0.96 },
      total: { value: "1500.00", confidence: 0.97 },
      sku: { value: "LIC-002", confidence: 0.91 },
    },
    {
      description: { value: "Cloud Hosting - Monthly", confidence: 0.94 },
      quantity: { value: "1", confidence: 0.99 },
      unit_price: { value: "1000.00", confidence: 0.95 },
      total: { value: "1000.00", confidence: 0.96 },
    },
  ],
  meta: {
    processing_time_ms: 1847,
    model_version: "invoice-parser-v2.1",
    warning: "Some fields extracted with confidence below 95%. Please verify accuracy.",
  },
}

export default function Page() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ErrorResponse | null>(null)
  const [invoiceData, setInvoiceData] = useState<InvoiceResponse | null>(null)

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file)
    setError(null)
    setInvoiceData(null)
    setLoading(true)

    try {
      const data = await parseInvoice(file)
      setInvoiceData(data)
    } catch (err) {
      if (err instanceof InvoiceParserError) {
        setError({
          code: err.code,
          message: err.message,
          details: err.details,
        })
      } else {
        setError({
          code: "UNKNOWN_ERROR",
          message: err instanceof Error ? err.message : "An unexpected error occurred",
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setError(null)
    setInvoiceData(null)
    setSelectedFile(null)
  }

  const handleDismissError = () => {
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="space-y-8">
          {!loading && !invoiceData && <FileUpload onFileSelect={handleFileSelect} disabled={loading} />}

          {loading && <LoadingSpinner />}

          {error && <ErrorDisplay error={error} onRetry={handleRetry} onDismiss={handleDismissError} />}

          {invoiceData && !loading && (
            <div className="space-y-4">
              <InvoiceDisplay data={invoiceData} />

              <div className="flex justify-center pt-4">
                <button
                  onClick={handleRetry}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                >
                  Parse Another Invoice
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
