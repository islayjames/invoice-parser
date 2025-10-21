"use client"

import type { InvoiceResponse } from "./formatted-view"

// Dynamic import for react-json-view to handle potential missing dependency
let ReactJson: any = null
try {
  ReactJson = require("react-json-view").default
} catch (e) {
  // Library not available, will use fallback
}

interface RawViewProps {
  data: InvoiceResponse
}

export function RawView({ data }: RawViewProps) {
  // If react-json-view is available, use it with configured options
  if (ReactJson) {
    return (
      <div className="bg-white border border-gray-200 p-6 rounded-lg overflow-auto max-h-[600px]">
        <ReactJson
          src={data}
          theme="rjv-default"
          collapsed={false}
          displayDataTypes={false}
          displayObjectSize={true}
          enableClipboard={true}
          name="invoice"
          indentWidth={2}
          iconStyle="triangle"
        />
      </div>
    )
  }

  // Fallback: render formatted JSON in a pre tag
  return (
    <div className="bg-white border border-gray-200 p-6 rounded-lg overflow-auto max-h-[600px]">
      <pre className="font-mono text-sm text-gray-800 whitespace-pre-wrap">{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
