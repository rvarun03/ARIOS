import type { RetrievalDebugItem } from '../types/api'

export default function RetrievedChunksDebug({ chunks }: { chunks: RetrievalDebugItem[] }) {
  return (
    <details className="details">
      <summary>Retrieval debug ({chunks.length} chunks)</summary>
      <div className="debug-list">
        {chunks.map((chunk, index) => {
          const score =
            chunk.hybrid_score ??
            chunk.keyword_score ??
            (chunk.distance != null ? `distance ${chunk.distance}` : '—')

          return (
            <article
              className="debug-card"
              key={`${chunk.chunk_id}-${index}`}
            >
              <div>
                <strong>
                  #{chunk.rank ?? index + 1} · Chunk {chunk.chunk_id ?? '—'}
                </strong>
                <span className="badge">
                  {chunk.retrieval_type || 'semantic'}
                </span>
              </div>
              <p className="muted">
                Index {chunk.chunk_index ?? '—'} · Score {score}
              </p>
              <p>{chunk.chunk_text_preview || 'No preview available.'}</p>
            </article>
          )
        })}
      </div>
    </details>
  )
}
