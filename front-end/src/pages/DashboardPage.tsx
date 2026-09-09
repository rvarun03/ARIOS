import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DocumentTable from '../components/DocumentTable'
import { ErrorMessage, LoadingState } from '../components/Feedback'
import PageHeader from '../components/PageHeader'
import { getDocuments } from '../lib/api'
import type { DocumentListItem } from '../types/api'

export default function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      setDocuments(await getDocuments())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load documents.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const sourceTypeCount = new Set(
    documents.map((document) => document.source_type),
  ).size
  const uploadedFileCount = documents.filter(
    (document) => document.file_name,
  ).length

  return (
    <>
      <PageHeader
        eyebrow="Knowledge library"
        title="Your documents"
        description="Browse everything ARIOS has analyzed and indexed."
        actions={
          <>
            <button
              className="button secondary"
              type="button"
              onClick={load}
              disabled={loading}
            >
              ↻ Refresh
            </button>
            <Link className="button" to="/ingest">
              Add document
            </Link>
          </>
        }
      />

      <section className="stat-strip">
        <div>
          <strong>{documents.length}</strong>
          <span>Total documents</span>
        </div>
        <div>
          <strong>{sourceTypeCount}</strong>
          <span>Source types</span>
        </div>
        <div>
          <strong>{uploadedFileCount}</strong>
          <span>Uploaded files</span>
        </div>
      </section>

      {error && <ErrorMessage message={error} />}
      {loading && <LoadingState label="Loading your documents…" />}
      {!loading && documents.length > 0 && (
        <DocumentTable documents={documents} />
      )}
      {!loading && documents.length === 0 && (
        <div className="empty">
          <div className="empty-icon">⌁</div>
          <h2>No documents yet</h2>
          <p>
            Ingest a URL or upload a PDF or image to start your research
            library.
          </p>
          <div>
            <Link className="button" to="/ingest">Ingest URL</Link>
            <Link className="button secondary" to="/upload">Upload file</Link>
          </div>
        </div>
      )}
    </>
  )
}
