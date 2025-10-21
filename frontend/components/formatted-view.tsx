import { InvoiceHeader } from "./invoice-header"
import { CustomerInfo } from "./customer-info"
import { LineItemsTable } from "./line-items-table"
import { PaymentSummary } from "./payment-summary"

interface Field {
  value: string
  confidence: number
}

interface InvoiceResponse {
  supplier: {
    name: Field
    address?: Field
    phone?: Field
    email?: Field
    tax_id?: Field
  }
  customer: {
    name: Field
    address?: Field
    account_id?: Field
  }
  invoice: {
    number: Field
    issue_date: Field
    due_date: Field
    po_number?: Field
    subtotal?: Field
    tax?: Field
    total: Field
    currency?: Field
    payment_terms?: Field
  }
  line_items: Array<{
    description: Field
    quantity: Field
    unit_price: Field
    total: Field
    sku?: Field
  }>
  meta: {
    processing_time_ms: number
    model_version: string
  }
}

interface FormattedViewProps {
  data: InvoiceResponse
}

export function FormattedView({ data }: FormattedViewProps) {
  const hasLineItems = data.line_items && data.line_items.length > 0

  return (
    <div className="bg-white border rounded-lg p-8 space-y-6 min-w-[800px]">
      {/* Invoice Header with Supplier and Invoice Metadata */}
      <InvoiceHeader supplier={data.supplier} invoice={data.invoice} />

      {/* Customer Bill To Information */}
      <CustomerInfo customer={data.customer} />

      {/* Line Items Table - Only render if items exist */}
      {hasLineItems && (
        <div className="border-t border-gray-200 pt-6">
          <LineItemsTable lineItems={data.line_items} currency={data.invoice.currency?.value} />
        </div>
      )}

      {/* Payment Summary with Totals */}
      <PaymentSummary invoice={data.invoice} />
    </div>
  )
}
