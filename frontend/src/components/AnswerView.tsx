import { AnswerResponse } from '../lib/api'
import { StatBadge } from './StatBadge'
import { CitationList } from './CitationList'

interface AnswerViewProps {
  answer: AnswerResponse
}

export function AnswerView({ answer }: AnswerViewProps) {
  return (
    <div className="space-y-6">
      {/* Answer */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Answer</h3>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed">{answer.answer}</p>
        </div>
      </div>

      {/* Metrics */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        <div className="flex flex-wrap gap-3">
          <StatBadge
            label="Input Tokens"
            value={answer.tokens_in}
            variant="info"
          />
          <StatBadge
            label="Output Tokens"
            value={answer.tokens_out}
            variant="info"
          />
          <StatBadge
            label="Cost"
            value={`$${parseFloat(answer.cost_usd).toFixed(6)}`}
            variant="warning"
          />
          <StatBadge
            label="Latency"
            value={answer.latency_ms}
            unit="ms"
            variant="default"
          />
          <StatBadge
            label="Model"
            value={answer.model}
            variant="default"
          />
          <StatBadge
            label="Provider"
            value={answer.provider}
            variant="default"
          />
          {answer.cached && (
            <StatBadge
              label="Cached"
              value="Yes"
              variant="success"
            />
          )}
        </div>
      </div>

      {/* Citations */}
      <div className="bg-white rounded-lg border p-6">
        <CitationList citations={answer.citations} />
      </div>
    </div>
  )
}