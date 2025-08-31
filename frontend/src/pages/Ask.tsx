import { useState } from 'react'
import { apiClient, AnswerRequest, AnswerResponse } from '../lib/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { AnswerView } from '../components/AnswerView'

export function Ask() {
  const [query, setQuery] = useState('')
  const [k, setK] = useState(5)
  const [maxContextTokens, setMaxContextTokens] = useState(2000)
  const [model, setModel] = useState('gpt-4o-mini')
  const [isLoading, setIsLoading] = useState(false)
  const [answer, setAnswer] = useState<AnswerResponse | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError('')
    setAnswer(null)

    try {
      const request: AnswerRequest = {
        query: query.trim(),
        k,
        max_context_tokens: maxContextTokens,
        model: model === 'default' ? undefined : model
      }

      const response = await apiClient.askRag(request)
      setAnswer(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get answer. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Ask Legal Questions</h1>
        <p className="mt-2 text-gray-600">
          Get AI-powered answers using your uploaded legal documents
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ask a Question</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <textarea
                id="query"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ask a legal question based on your uploaded documents..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="k" className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Sources (k)
                </label>
                <Input
                  id="k"
                  type="number"
                  min="1"
                  max="20"
                  value={k}
                  onChange={(e) => setK(parseInt(e.target.value))}
                />
              </div>

              <div>
                <label htmlFor="maxContextTokens" className="block text-sm font-medium text-gray-700 mb-2">
                  Max Context Tokens
                </label>
                <Input
                  id="maxContextTokens"
                  type="number"
                  min="100"
                  max="8000"
                  value={maxContextTokens}
                  onChange={(e) => setMaxContextTokens(parseInt(e.target.value))}
                />
              </div>

              <div>
                <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-2">
                  Model
                </label>
                <select
                  id="model"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                >
                  <option value="default">Default (gpt-4o-mini)</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </select>
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="w-full"
            >
              {isLoading ? 'Getting Answer...' : 'Ask Question'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {answer && (
        <div className="mt-8">
          <AnswerView answer={answer} />
        </div>
      )}
    </div>
  )
}