interface PaymentSummaryProps {
  invoice: {
    subtotal?: { value: number; confidence: number }
    tax?: { value: number; confidence: number }
    total: { value: number; confidence: number }
    currency: { value: string; confidence: number }
    payment_terms?: { value: string; confidence: number }
  }
}

export function PaymentSummary({ invoice }: PaymentSummaryProps) {
  const formatCurrency = (amount: number): string => {
    return amount.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  return (
    <div className="ml-auto max-w-sm bg-gray-50 border-t border-gray-200 pt-4 px-6 pb-6">
      <div className="text-right space-y-1">
        {invoice.subtotal?.value && (
          <div className="text-base text-gray-700">Subtotal: ${formatCurrency(invoice.subtotal.value)}</div>
        )}

        {invoice.tax?.value && <div className="text-base text-gray-700">Tax: ${formatCurrency(invoice.tax.value)}</div>}

        <div className="text-xl font-bold text-gray-900 border-t border-gray-300 pt-2 mt-2">
          Total: ${formatCurrency(invoice.total.value)} {invoice.currency.value}
        </div>
      </div>

      {invoice.payment_terms?.value && (
        <div className="text-sm italic text-gray-600 mt-3 text-right">Payment Terms: {invoice.payment_terms.value}</div>
      )}
    </div>
  )
}
