"use client"

import { useState, useRef, type DragEvent, type ChangeEvent } from "react"
import { CloudUpload, X, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileUploadProps {
  onFileSelect: (file: File) => void
  disabled?: boolean
  acceptedFormats?: string[]
  maxSizeMB?: number
}

const DEFAULT_ACCEPTED_FORMATS = [
  ".pdf",
  ".jpg",
  ".jpeg",
  ".png",
  ".tiff",
  ".tif",
  ".bmp",
  ".webp",
  ".heic",
  ".heif",
  ".gif",
  ".txt",
  ".md",
]

export function FileUpload({
  onFileSelect,
  disabled = false,
  acceptedFormats = DEFAULT_ACCEPTED_FORMATS,
  maxSizeMB = 5,
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [error, setError] = useState<string>("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const maxSizeBytes = maxSizeMB * 1024 * 1024

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxSizeBytes) {
      return `File size exceeds ${maxSizeMB}MB limit`
    }

    // Check file extension
    const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()
    if (!acceptedFormats.includes(fileExtension)) {
      return `File type not supported. Please upload: ${acceptedFormats.join(", ")}`
    }

    return null
  }

  const handleFile = (file: File) => {
    setError("")
    const validationError = validateFile(file)

    if (validationError) {
      setError(validationError)
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
    onFileSelect(file)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled) {
      setIsDragOver(true)
    }
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    if (disabled) return

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleRemove = () => {
    setSelectedFile(null)
    setError("")
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  return (
    <div className="w-full">
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative min-h-[280px] flex flex-col items-center justify-center
          border-2 border-dashed rounded-lg p-8 transition-all duration-200
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          ${isDragOver ? "border-blue-600 bg-blue-100" : "border-gray-300 hover:border-blue-400 hover:bg-blue-50/50"}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats.join(",")}
          onChange={handleFileInputChange}
          disabled={disabled}
          className="hidden"
        />

        {!selectedFile ? (
          <>
            <CloudUpload className="w-16 h-16 text-gray-400 mb-4" />
            <p className="text-base font-medium text-gray-700 mb-2 text-center">
              Drag and drop your invoice here, or click to browse
            </p>
            <p className="text-sm text-muted-foreground text-center">
              Supports PDF, images (JPG, PNG, etc.), and text files up to {maxSizeMB}MB
            </p>
          </>
        ) : (
          <div className="flex flex-col items-center space-y-4 w-full max-w-md">
            <FileText className="w-12 h-12 text-blue-600" />
            <div className="text-center w-full">
              <p className="text-base font-medium text-gray-900 break-all">{selectedFile.name}</p>
              <p className="text-sm text-gray-600 mt-1">{formatFileSize(selectedFile.size)}</p>
            </div>
            <Button
              onClick={(e) => {
                e.stopPropagation()
                handleRemove()
              }}
              variant="outline"
              size="sm"
              className="mt-2"
            >
              <X className="w-4 h-4 mr-1" />
              Remove
            </Button>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 text-sm text-red-600 flex items-start">
          <span className="font-medium">Error:</span>
          <span className="ml-1">{error}</span>
        </div>
      )}
    </div>
  )
}
