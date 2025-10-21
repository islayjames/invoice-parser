"use client"

import { Button } from "@/components/ui/button"
import { Copy } from "lucide-react"

interface ControlBarProps {
  viewMode: "formatted" | "raw"
  onViewModeChange: (mode: "formatted" | "raw") => void
  onCopy: () => void
}

export function ControlBar({ viewMode, onViewModeChange, onCopy }: ControlBarProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 py-3 px-4 border-b border-gray-200 bg-white">
      {/* View Toggle Buttons */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
        <Button
          onClick={() => onViewModeChange("formatted")}
          className={`flex-1 sm:flex-none transition-all ${
            viewMode === "formatted"
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-white text-gray-700 hover:bg-gray-50"
          }`}
          variant={viewMode === "formatted" ? "default" : "ghost"}
        >
          Formatted View
        </Button>
        <Button
          onClick={() => onViewModeChange("raw")}
          className={`flex-1 sm:flex-none transition-all ${
            viewMode === "raw" ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-white text-gray-700 hover:bg-gray-50"
          }`}
          variant={viewMode === "raw" ? "default" : "ghost"}
        >
          Raw JSON
        </Button>
      </div>

      {/* Copy Button */}
      <Button onClick={onCopy} variant="outline" className="flex items-center gap-2 bg-transparent">
        <Copy className="w-4 h-4" />
        Copy JSON
      </Button>
    </div>
  )
}
