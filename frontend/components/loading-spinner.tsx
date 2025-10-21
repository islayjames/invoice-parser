import { Loader2 } from "lucide-react"

interface LoadingSpinnerProps {
  message?: string
  showEstimate?: boolean
}

export function LoadingSpinner({ message = "Processing your invoice...", showEstimate = true }: LoadingSpinnerProps) {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
        <div className="flex flex-col items-center gap-2">
          <p className="text-lg font-medium">{message}</p>
          {showEstimate && <p className="text-sm text-muted-foreground">This may take up to 20 seconds</p>}
        </div>
      </div>
    </div>
  )
}
