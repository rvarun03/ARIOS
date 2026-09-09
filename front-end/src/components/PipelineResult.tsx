import { Link } from 'react-router-dom'
import type { PipelineResponse } from '../types/api'

const fields: Array<[keyof PipelineResponse, string]> = [
  ['document_id', 'Document ID'], ['title', 'Title'], ['source_type', 'Source type'],
  ['source_url', 'Source URL'], ['file_name', 'File name'], ['file_type', 'File type'],
  ['file_size', 'File size'], ['cleaned_text_length', 'Cleaned text'], ['document_type', 'Document type'],
  ['indexed', 'Indexed'], ['chunk_count', 'Chunks'], ['stored_vector_count', 'Stored vectors'],
]

export default function PipelineResult({ result }: { result: PipelineResponse }) {
  const succeeded = result.success && !result.error
  const description =
    result.error ||
    (result.indexed
      ? 'Saved and indexed successfully.'
      : 'The document was processed.')

  return (
    <section
      className={`pipeline-result ${
        succeeded ? 'success-result' : 'failure-result'
      }`}
    >
      <div className="result-title">
        <span>{succeeded ? '✓' : '!'}</span>
        <div>
          <h2>{succeeded ? 'Document ready' : 'Processing incomplete'}</h2>
          <p>{description}</p>
        </div>
      </div>

      <dl>
        {fields.map(([key, label]) => {
          const value = result[key]
          if (value === undefined || value === null) return null

          return (
            <div key={key}>
              <dt>{label}</dt>
              <dd>
                {typeof value === 'boolean'
                  ? value ? 'Yes' : 'No'
                  : String(value)}
              </dd>
            </div>
          )
        })}
      </dl>

      {result.document_id != null && (
        <Link className="button" to={`/ask?document_id=${result.document_id}`}>
          Ask this document
        </Link>
      )}
    </section>
  )
}
