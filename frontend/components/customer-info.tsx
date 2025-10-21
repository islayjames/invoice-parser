interface Field {
  value: string
  confidence: number
}

interface CustomerInfoProps {
  customer: {
    name: Field
    address?: Field
    account_id?: Field
  }
}

export function CustomerInfo({ customer }: CustomerInfoProps) {
  return (
    <div className="bg-gray-50 border-l-4 border-blue-500 p-4 rounded-r">
      <h3 className="text-sm font-semibold text-gray-700 uppercase mb-2">Bill To:</h3>
      <div className="space-y-1">
        <p className="text-lg font-bold text-gray-900">{customer.name.value}</p>
        {customer.address?.value && (
          <p className="text-sm text-gray-600 whitespace-pre-line">{customer.address.value}</p>
        )}
        {customer.account_id?.value && <p className="text-sm text-gray-600">Account: {customer.account_id.value}</p>}
      </div>
    </div>
  )
}
