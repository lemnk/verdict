import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { apiClient, DocumentResponse } from '../lib/api'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export function Document() {
  const { docId } = useParams<{ docId: string }>()
  const [searchParams] = useSearchParams()
  const [document, setDocument] = useState<DocumentResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [highlightedChunk, setHighlightedChunk] = useState<number | null>(null)

  useEffect(() => {
    if (docId) {
      loadDocument(docId)
    }
  }, [docId])

  useEffect(() => {
    const chunkParam = searchParams.get('chunk')
    if (chunkParam) {
      setHighlightedChunk(parseInt(chunkParam))
    }
  }, [searchParams])

  const loadDocument = async (id: string) => {
    try {
      const response = await apiClient.getDocument(id)
      setDocument(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load document')
    } finally {
      setIsLoading(false)
    }
  }

  const filteredChunks = document?.chunks.filter(chunk =>
    chunk.content.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">Loading document...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">Document not found</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Document Chunks</h1>
        <p className="mt-2 text-gray-600">
          Document ID: {document.doc_id} | Total Chunks: {document.total_chunks}
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Search Chunks</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            type="text"
            placeholder="Search within chunks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredChunks.map((chunk) => (
          <Card
            key={chunk.id}
            className={`transition-all ${
              highlightedChunk === chunk.chunk_index
                ? 'ring-2 ring-blue-500 bg-blue-50'
                : ''
            }`}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  Chunk {chunk.chunk_index}
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    Embedding: {chunk.embedding_length} dimensions
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const url = new URL(window.location.href)
                      url.searchParams.set('chunk', chunk.chunk_index.toString())
                      window.history.pushState({}, '', url.toString())
                      setHighlightedChunk(chunk.chunk_index)
                    }}
                  >
                    Highlight
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {chunk.content}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredChunks.length === 0 && searchTerm && (
        <div className="text-center py-8 text-gray-500">
          No chunks found matching "{searchTerm}"
        </div>
      )}
    </div>
  )
}