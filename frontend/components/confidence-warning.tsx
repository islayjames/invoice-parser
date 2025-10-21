"use client"

import { AlertTriangle, X } from "lucide-react"

interface ConfidenceWarningProps {
  message: string
  onDismiss?: () => void
}

export function ConfidenceWarning({ message, onDismiss }: ConfidenceWarningProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-300 border-l-4 border-l-yellow-500 p-4 rounded-md">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1 text-sm text-yellow-800 leading-relaxed">{message}</div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 text-yellow-600 hover:text-yellow-800 transition-colors"
            aria-label="Dismiss warning"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  )
}
