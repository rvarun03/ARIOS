import type { AskResponse } from '../types/api'
import JsonBlock from './JsonBlock'
import RetrievedChunksDebug from './RetrievedChunksDebug'

export default function AnswerPanel({ result }: { result: AskResponse }) {
  return (
    <section className="answer-panel" aria-live="polite">
      <div className="eyebrow">Answer</div>
      <p className="answer-text">{result.answer}</p>

      <div className="answer-meta">
        {result.retrieval_mode && (
          <span><b>Retrieval</b> {result.retrieval_mode}</span>
        )}
        {typeof result.metadata_used === 'boolean' && (
          <span>
            <b>Metadata</b> {result.metadata_used ? 'used' : 'not used'}
          </span>
        )}
      </div>

      {result.expanded_queries && result.expanded_queries.length > 0 && (
        <div className="result-section">
          <h3>Expanded queries</h3>
          <ul>
            {result.expanded_queries.map((query) => (
              <li key={query}>{query}</li>
            ))}
          </ul>
        </div>
      )}

      {result.evaluation && (
        <details className="details">
          <summary>Evaluation</summary>
          <JsonBlock value={result.evaluation} />
        </details>
      )}

      {result.retrieval_debug && (
        <RetrievedChunksDebug chunks={result.retrieval_debug} />
      )}
    </section>
  )
}
