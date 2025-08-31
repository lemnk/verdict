import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Citation } from '../lib/api'
import { Button } from './ui/Button'

interface CitationListProps {
  citations: Citation[]
}

export function CitationList({ citations }: CitationListProps) {
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set())
  const navigate = useNavigate()

  const toggleCitation = (index: number) => {
    const newExpanded = new Set(expandedCitations)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedCitations(newExpanded)
  }

  const navigateToDocument = (docId: string, chunkIndex: number) => {
    navigate(`/document/${docId}?chunk=${chunkIndex}`)
  }

  if (citations.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No citations available
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Sources</h3>
      <div className="space-y-3">
        {citations.map((citation, index) => (
          <div key={index} className="border rounded-lg p-4 bg-gray-50">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    {index + 1}
                  </span>
                  <span className="text-sm text-gray-600">
                    Document: {citation.doc_id.slice(0, 8)}... | Chunk: {citation.chunk_index}
                  </span>
                  <span className="text-sm text-gray-500">
                    Score: {citation.score.toFixed(3)}
                  </span>
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-700">
                    {expandedCitations.has(index) 
                      ? citation.snippet 
                      : `${citation.snippet.slice(0, 200)}...`
                    }
                  </p>
                  
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => toggleCitation(index)}
                    >
                      {expandedCitations.has(index) ? 'Show Less' : 'Show More'}
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigateToDocument(citation.doc_id, citation.chunk_index)}
                    >
                      View in Document
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}