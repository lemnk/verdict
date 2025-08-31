import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/api'
import { FileUploader } from '../components/FileUploader'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'

export function Upload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedDocId, setUploadedDocId] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isParsing, setIsParsing] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setUploadedDocId(null)
    setError('')
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setError('')

    try {
      const response = await apiClient.uploadPdf(selectedFile)
      setUploadedDocId(response.id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleParse = async () => {
    if (!uploadedDocId) return

    setIsParsing(true)
    setError('')

    try {
      await apiClient.parseDocument(uploadedDocId)
      // Navigate to document view after successful parsing
      navigate(`/document/${uploadedDocId}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Parsing failed. Please try again.')
    } finally {
      setIsParsing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload Document</h1>
        <p className="mt-2 text-gray-600">
          Upload a PDF legal document to extract precedents and enable RAG search
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select PDF Document</CardTitle>
        </CardHeader>
        <CardContent>
          <FileUploader onFileSelect={handleFileSelect} disabled={isUploading} />
          
          {selectedFile && (
            <div className="mt-6">
              <Button
                onClick={handleUpload}
                disabled={isUploading}
                className="w-full"
              >
                {isUploading ? 'Uploading...' : 'Upload Document'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {uploadedDocId && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Document Uploaded Successfully</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-green-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-green-800 font-medium">
                    Document ID: {uploadedDocId}
                  </span>
                </div>
              </div>
              
              <div className="flex space-x-4">
                <Button
                  onClick={handleParse}
                  disabled={isParsing}
                  className="flex-1"
                >
                  {isParsing ? 'Parsing...' : 'Parse Document Now'}
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => navigate(`/document/${uploadedDocId}`)}
                  className="flex-1"
                >
                  View Document
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}