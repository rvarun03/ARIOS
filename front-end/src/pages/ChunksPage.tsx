import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ErrorMessage, LoadingState } from '../components/Feedback'
import PageHeader from '../components/PageHeader'
import { getChunksByDocument } from '../lib/api'
import type { DocumentChunksResponse } from '../types/api'

export default function ChunksPage() {
  const { documentId } = useParams()
  const [data, setData] = useState<DocumentChunksResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!documentId) return

    getChunksByDocument(Number(documentId))
      .then(setData)
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Unable to load chunks.')
      })
  }, [documentId])

  return (
    <>
      <PageHeader
        eyebrow="Index inspection"
        title={data?.title || `Document #${documentId}`}
        description={
          data
            ? `${data.chunk_count} indexed chunks`
            : 'Loading indexed content…'
        }
        actions={
          <Link
            className="button secondary"
            to={`/ask?document_id=${documentId}`}
          >
            Ask this document
          </Link>
        }
      />

      {error && <ErrorMessage message={error} />}
      {!data && !error && <LoadingState />}

      {data && (
        <div className="chunks-list">
          {data.chunks.map((chunk) => (
            <article className="chunk-card" key={chunk.chunk_id}>
              <div>
                <strong>Chunk {chunk.chunk_index}</strong>
                <span>
                  #{chunk.chunk_id} · {chunk.word_count} words ·{' '}
                  {chunk.char_count} characters
                </span>
              </div>
              <p>{chunk.chunk_text}</p>
            </article>
          ))}
        </div>
      )}
    </>
  )
}
