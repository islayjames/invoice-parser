"use client"

import { useState } from "react"
import { AlertCircle, ChevronDown, ChevronUp } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"

interface ErrorDisplayProps {
  error: {
    code: string
    message: string
    details?: Record<string, any>
  }
  onRetry?: () => void
  onDismiss?: () => void
}

export function ErrorDisplay({ error, onRetry, onDismiss }: ErrorDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Alert className="bg-red-50 border-red-200 border-l-4 border-l-red-500">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />

        <div className="flex-1 space-y-3 min-w-0">
          <AlertDescription className="space-y-2">
            <div className="text-xs font-bold text-red-700 uppercase tracking-wide">{error.code}</div>
            <div className="text-base text-red-800 font-medium break-words overflow-wrap-anywhere">{error.message}</div>
          </AlertDescription>

          {error.details && Object.keys(error.details).length > 0 && (
            <div className="space-y-2">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-1 text-sm text-red-700 hover:text-red-800 font-medium transition-colors"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="h-4 w-4" />
                    Hide Details
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4" />
                    Show Details
                  </>
                )}
              </button>

              {isExpanded && (
                <div className="bg-red-100 border border-red-200 rounded-md p-3 animate-in slide-in-from-top-2 duration-200">
                  <pre className="text-xs text-red-900 font-mono overflow-x-auto whitespace-pre-wrap break-words">
                    {JSON.stringify(error.details, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {(onRetry || onDismiss) && (
            <div className="flex gap-2 pt-2">
              {onRetry && (
                <Button onClick={onRetry} size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                  Try Again
                </Button>
              )}
              {onDismiss && (
                <Button
                  onClick={onDismiss}
                  size="sm"
                  variant="outline"
                  className="border-gray-300 text-gray-700 hover:bg-gray-50 bg-transparent"
                >
                  Dismiss
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </Alert>
  )
}
