interface InvoiceField {
  value: string
  confidence: number
}

interface InvoiceMetaInfoProps {
  invoice: {
    number?: InvoiceField
    issue_date?: InvoiceField
    due_date?: InvoiceField
    po_number?: InvoiceField
  }
}

// Helper function to format dates from YYYY-MM-DD to readable format
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

export function InvoiceMetaInfo({ invoice }: InvoiceMetaInfoProps) {
  return (
    <div className="text-right">
      <h2 className="text-3xl font-bold uppercase text-gray-900 mb-4">INVOICE</h2>
      <div className="space-y-1">
        {invoice.number?.value && (
          <div className="text-sm">
            <span className="text-gray-600">Invoice Number: </span>
            <span className="font-semibold text-gray-900">{invoice.number.value}</span>
          </div>
        )}
        {invoice.issue_date?.value && (
          <div className="text-sm">
            <span className="text-gray-600">Issue Date: </span>
            <span className="font-semibold text-gray-900">{formatDate(invoice.issue_date.value)}</span>
          </div>
        )}
        {invoice.due_date?.value && (
          <div className="text-sm">
            <span className="text-gray-600">Due Date: </span>
            <span className="font-semibold text-gray-900">{formatDate(invoice.due_date.value)}</span>
          </div>
        )}
        {invoice.po_number?.value && (
          <div className="text-sm">
            <span className="text-gray-600">PO Number: </span>
            <span className="font-semibold text-gray-900">{invoice.po_number.value}</span>
          </div>
        )}
      </div>
    </div>
  )
}
