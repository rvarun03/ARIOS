import type {
  AskRequest,
  AskResponse,
  DocumentChunksResponse,
  DocumentListItem,
  IngestResponse,
  UploadResponse,
} from '../types/api'
import { API_BASE_URL } from '../config'

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options)
  } catch {
    throw new ApiError('Could not reach the ARIOS backend. Check that it is running and the API URL is correct.')
  }

  const contentType = response.headers.get('content-type') || ''
  const body = contentType.includes('application/json') ? await response.json() : await response.text()
  if (!response.ok) {
    const detail = typeof body === 'object' && body && 'detail' in body ? body.detail : body
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || JSON.stringify(item)).join('; ')
      : typeof detail === 'string' ? detail : `Request failed (${response.status})`
    throw new ApiError(message, response.status)
  }
  return body as T
}

export const getDocuments = () => request<DocumentListItem[]>('/documents')
export const getDocumentById = (id: number) => request<DocumentListItem>(`/documents/${id}`)
export const getChunksByDocument = (id: number) => request<DocumentChunksResponse>(`/documents/${id}/chunks`)

export const ingestSource = (source: string) => request<IngestResponse>('/documents/graph/ingest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ source }),
})

export function uploadDocument(file: File) {
  const data = new FormData()
  data.append('file', file)
  return request<UploadResponse>('/documents/graph/upload', { method: 'POST', body: data })
}

export const askDocument = (payload: AskRequest) => request<AskResponse>('/documents/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
})
