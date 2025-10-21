import { SupplierInfo } from "./supplier-info"
import { InvoiceMetaInfo } from "./invoice-meta-info"

interface Field {
  value: string
  confidence: number
}

interface InvoiceHeaderProps {
  supplier: {
    name: Field
    address?: Field
    phone?: Field
    email?: Field
    tax_id?: Field
  }
  invoice: {
    number: Field
    issue_date: Field
    due_date: Field
    po_number?: Field
  }
}

export function InvoiceHeader({ supplier, invoice }: InvoiceHeaderProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 pb-6 border-b border-gray-200">
      <div>
        <SupplierInfo supplier={supplier} />
      </div>
      <div>
        <InvoiceMetaInfo invoice={invoice} />
      </div>
    </div>
  )
}
