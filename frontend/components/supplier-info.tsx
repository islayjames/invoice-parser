interface SupplierField {
  value: string
  confidence: number
}

interface SupplierInfoProps {
  supplier: {
    name: SupplierField
    address?: SupplierField
    phone?: SupplierField
    email?: SupplierField
    tax_id?: SupplierField
  }
}

export function SupplierInfo({ supplier }: SupplierInfoProps) {
  return (
    <div className="flex flex-col space-y-1">
      {/* Supplier name - always displayed */}
      {supplier.name?.value && (
        <h3 className="text-2xl font-bold text-gray-900 leading-relaxed">{supplier.name.value}</h3>
      )}

      {/* Address - multi-line support */}
      {supplier.address?.value && (
        <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{supplier.address.value}</p>
      )}

      {/* Phone */}
      {supplier.phone?.value && <p className="text-sm text-gray-600 leading-relaxed">Phone: {supplier.phone.value}</p>}

      {/* Email */}
      {supplier.email?.value && <p className="text-sm text-gray-600 leading-relaxed">Email: {supplier.email.value}</p>}

      {/* Tax ID */}
      {supplier.tax_id?.value && (
        <p className="text-sm text-gray-600 leading-relaxed">Tax ID: {supplier.tax_id.value}</p>
      )}
    </div>
  )
}
