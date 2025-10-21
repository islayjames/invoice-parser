interface LineItemField {
  value: string | number
  confidence: number
}

interface LineItem {
  sku?: LineItemField
  description: LineItemField
  quantity: LineItemField
  unit_price: LineItemField
  discount?: LineItemField
  tax_rate?: LineItemField
  total: LineItemField
}

interface LineItemsTableProps {
  lineItems: LineItem[]
  currency?: string
}

export function LineItemsTable({ lineItems, currency = "USD" }: LineItemsTableProps) {
  // Check if any line item has SKU
  const hasSku = lineItems.some((item) => item.sku?.value)

  // Format currency values
  const formatCurrency = (value: string | number): string => {
    const numValue = typeof value === "string" ? Number.parseFloat(value) : value
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
    }).format(numValue)
  }

  // Format quantity (show as integer if whole number, otherwise decimal)
  const formatQuantity = (value: string | number): string => {
    const numValue = typeof value === "string" ? Number.parseFloat(value) : value
    return Number.isInteger(numValue) ? numValue.toString() : numValue.toFixed(2)
  }

  if (lineItems.length === 0) {
    return <div className="text-center py-8 text-gray-500">No line items</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse border border-gray-200">
        <thead>
          <tr className="bg-gray-100">
            {hasSku && (
              <th className="p-3 text-left text-sm font-semibold text-gray-700 border border-gray-200">SKU</th>
            )}
            <th className="p-3 text-left text-sm font-semibold text-gray-700 border border-gray-200">Description</th>
            <th className="p-3 text-right text-sm font-semibold text-gray-700 border border-gray-200">Quantity</th>
            <th className="p-3 text-right text-sm font-semibold text-gray-700 border border-gray-200">Unit Price</th>
            <th className="p-3 text-right text-sm font-semibold text-gray-700 border border-gray-200">Total</th>
          </tr>
        </thead>
        <tbody>
          {lineItems.map((item, index) => (
            <tr
              key={index}
              className={`hover:bg-gray-100 transition-colors ${index % 2 === 0 ? "bg-white" : "bg-gray-50"}`}
            >
              {hasSku && (
                <td className="p-3 text-left text-sm text-gray-600 border border-gray-200">{item.sku?.value || "-"}</td>
              )}
              <td className="p-3 text-left text-sm text-gray-900 border border-gray-200">{item.description.value}</td>
              <td className="p-3 text-right text-sm text-gray-900 border border-gray-200">
                {formatQuantity(item.quantity.value)}
              </td>
              <td className="p-3 text-right text-sm text-gray-900 border border-gray-200">
                {formatCurrency(item.unit_price.value)}
              </td>
              <td className="p-3 text-right text-sm font-semibold text-gray-900 border border-gray-200">
                {formatCurrency(item.total.value)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
