import axios, { AxiosInstance } from 'axios'
import { getToken, removeToken } from './auth'

// Types matching backend models
export interface UserLogin {
  email: string
  password: string
}

export interface UserResponse {
  id: number
  email: string
  name: string
  access_token: string
  role: string
}

export interface DocumentUploadResponse {
  id: string
  status: string
}

export interface ParseResult {
  doc_id: string
  chunks_indexed: number
  total_chunks: number
  status: string
}

export interface AnswerRequest {
  query: string
  k?: number
  max_context_tokens?: number
  model?: string
}

export interface Citation {
  doc_id: string
  chunk_index: number
  snippet: string
  score: number
}

export interface AnswerResponse {
  answer: string
  citations: Citation[]
  provider: string
  model: string
  tokens_in: number
  tokens_out: number
  cost_usd: string
  latency_ms: number
  cached: boolean
}

export interface QueryLog {
  id: string
  user_id: number
  user_name?: string
  query: string
  provider: string
  model: string
  tokens_in: number
  tokens_out: number
  cost_usd: string
  latency_ms: number
  created_at: string
  cached: boolean
}

export interface DocumentChunk {
  id: string
  chunk_index: number
  content: string
  embedding_length: number
}

export interface DocumentResponse {
  doc_id: string
  chunks: DocumentChunk[]
  total_chunks: number
}

// Metrics types
export interface ModelMetrics {
  model: string
  n: number
  avg_cost_usd: number
  p95_latency_ms: number
}

export interface HourlyMetrics {
  ts_hour: string
  n: number
  avg_cost_usd: number
  avg_latency_ms: number
}

export interface MetricsSummary {
  total_queries: number
  cache_hit_rate: number
  avg_cost_usd: number
  p50_latency_ms: number
  p95_latency_ms: number
  by_model: ModelMetrics[]
  last_24h: HourlyMetrics[]
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add auth interceptor
    this.client.interceptors.request.use((config) => {
      const token = getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          removeToken()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  async login(credentials: UserLogin): Promise<UserResponse> {
    const response = await this.client.post('/api/auth/login', credentials)
    return response.data
  }

  async uploadPdf(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await this.client.post('/api/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async parseDocument(docId: string): Promise<ParseResult> {
    const response = await this.client.post(`/api/parse/${docId}`)
    return response.data
  }

  async askRag(body: AnswerRequest): Promise<AnswerResponse> {
    const response = await this.client.post('/api/rag/ask', body)
    return response.data
  }

  async listUserHistory(): Promise<{ items: QueryLog[] }> {
    const response = await this.client.get('/api/rag/history')
    return response.data
  }

  async getDocument(docId: string): Promise<DocumentResponse> {
    const response = await this.client.get(`/api/parse/${docId}/chunks`)
    return response.data
  }

  // Admin metrics endpoints
  async getMetricsSummary(): Promise<MetricsSummary> {
    const response = await this.client.get('/api/metrics/summary')
    return response.data
  }

  async getRecentQueries(limit: number = 100): Promise<{ items: QueryLog[] }> {
    const response = await this.client.get(`/api/metrics/recent?limit=${limit}`)
    return response.data
  }
}

export const apiClient = new ApiClient()