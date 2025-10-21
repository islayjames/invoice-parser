"use client"

import { useState } from "react"
import { ControlBar } from "./control-bar"
import { ConfidenceWarning } from "./confidence-warning"
import { FormattedView } from "./formatted-view"
import { RawView } from "./raw-view"
import { useToast } from "@/hooks/use-toast"

interface InvoiceResponse {
  supplier: {
    name: { value: string; confidence: number }
    address?: { value: string; confidence: number }
    phone?: { value: string; confidence: number }
    email?: { value: string; confidence: number }
    tax_id?: { value: string; confidence: number }
  }
  customer: {
    name: { value: string; confidence: number }
    address?: { value: string; confidence: number }
    account_id?: { value: string; confidence: number }
  }
  invoice: {
    number: { value: string; confidence: number }
    issue_date: { value: string; confidence: number }
    due_date?: { value: string; confidence: number }
    po_number?: { value: string; confidence: number }
    subtotal?: { value: number; confidence: number }
    tax?: { value: number; confidence: number }
    total: { value: number; confidence: number }
    currency?: { value: string; confidence: number }
    payment_terms?: { value: string; confidence: number }
  }
  line_items: Array<{
    description: { value: string; confidence: number }
    quantity: { value: number; confidence: number }
    unit_price: { value: number; confidence: number }
    total: { value: number; confidence: number }
    sku?: { value: string; confidence: number }
  }>
  meta: {
    processing_time_ms: number
    model_version: string
    warning?: string
  }
}

interface InvoiceDisplayProps {
  data: InvoiceResponse
}

export function InvoiceDisplay({ data }: InvoiceDisplayProps) {
  const [viewMode, setViewMode] = useState<"formatted" | "raw">("formatted")
  const { toast } = useToast()

  const handleCopy = async () => {
    try {
      const jsonString = JSON.stringify(data, null, 2)
      await navigator.clipboard.writeText(jsonString)

      toast({
        title: "Copied to clipboard",
        description: "Invoice data has been copied to your clipboard.",
      })
    } catch (error) {
      console.error("Failed to copy to clipboard:", error)

      toast({
        title: "Copy failed",
        description: "Failed to copy invoice data to clipboard. Please try again.",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="max-w-5xl mx-auto bg-white border rounded-lg shadow-sm">
      <ControlBar viewMode={viewMode} onViewModeChange={setViewMode} onCopy={handleCopy} />

      <div className="p-6 space-y-4">
        {data.meta.warning && <ConfidenceWarning message={data.meta.warning} />}

        {viewMode === "formatted" ? <FormattedView data={data} /> : <RawView data={data} />}
      </div>
    </div>
  )
}
