export interface DocumentStatistics {
  [key: string]: unknown
}

export interface DocumentListItem {
  document_id: number
  title: string
  source_type: string
  source_url?: string | null
  file_name?: string | null
  file_path?: string | null
  statistics?: DocumentStatistics
  created_at?: string | null
}

export interface PipelineResponse {
  success: boolean
  is_valid?: boolean
  document_id?: number | null
  title?: string | null
  source_type?: string | null
  source_url?: string | null
  source?: string | null
  file_name?: string | null
  file_type?: string | null
  file_size?: number | null
  cleaned_text_length?: number
  document_type?: string | null
  document_type_confidence?: number
  saved_to_db?: boolean
  indexed?: boolean
  chunk_count?: number
  stored_vector_count?: number
  indexing_result?: unknown
  error?: string | null
  [key: string]: unknown
}

export type IngestResponse = PipelineResponse
export type UploadResponse = PipelineResponse

export interface AskRequest {
  question: string
  top_k: number
  source_type: string | null
  document_id: number | null
}

export interface RetrievalDebugItem {
  rank?: number
  document_id?: number
  chunk_id?: number
  chunk_index?: number
  title?: string
  retrieval_type?: string | null
  retrieval_types?: string[] | null
  distance?: number | null
  keyword_score?: number | null
  hybrid_score?: number | null
  chunk_text_preview?: string
  [key: string]: unknown
}

export interface AskResponse {
  question: string
  answer: string
  metadata_used?: boolean
  evaluation?: Record<string, unknown>
  expanded_queries?: string[] | null
  retrieval_mode?: string | null
  retrieval_debug?: RetrievalDebugItem[]
  source_count?: number
  sources?: unknown[]
}

export interface DocumentChunk {
  chunk_id: number
  chunk_index: number
  chunk_text: string
  word_count: number
  char_count: number
}

export interface DocumentChunksResponse {
  document_id: number
  title: string
  chunk_count: number
  chunks: DocumentChunk[]
}
