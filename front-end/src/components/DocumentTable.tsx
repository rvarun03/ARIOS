import { Link } from 'react-router-dom'
import type { DocumentListItem } from '../types/api'

function formatDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

export default function DocumentTable({ documents }: { documents: DocumentListItem[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Document</th>
            <th>Source</th>
            <th>Statistics</th>
            <th>Created</th>
            <th><span className="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((document) => {
            const source =
              document.source_url ||
              document.file_name ||
              document.file_path ||
              'No source details'
            const statistics = document.statistics
              ? Object.entries(document.statistics)
                  .slice(0, 2)
                  .map(([key, value]) => `${key}: ${String(value)}`)
                  .join(' · ')
              : '—'

            return (
              <tr key={document.document_id}>
                <td className="muted">#{document.document_id}</td>
                <td>
                  <strong>{document.title || 'Untitled document'}</strong>
                  <span className="cell-subtitle">{source}</span>
                </td>
                <td><span className="badge">{document.source_type}</span></td>
                <td className="muted">{statistics || '—'}</td>
                <td className="muted">{formatDate(document.created_at)}</td>
                <td>
                  <div className="row-actions">
                    <Link
                      className="button small"
                      to={`/ask?document_id=${document.document_id}`}
                    >
                      Ask
                    </Link>
                    <Link
                      className="button small secondary"
                      to={`/documents/${document.document_id}/chunks`}
                    >
                      Chunks
                    </Link>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
