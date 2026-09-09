import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import AnswerPanel from '../components/AnswerPanel'
import { ErrorMessage, LoadingState } from '../components/Feedback'
import PageHeader from '../components/PageHeader'
import SubmitButton from '../components/SubmitButton'
import { askDocument, getDocuments } from '../lib/api'
import type { AskResponse, DocumentListItem } from '../types/api'

const LAST_DOCUMENT_KEY = 'arios:last-document-id'

export default function AskPage() {
  const [params] = useSearchParams()
  const [documents, setDocuments] = useState<DocumentListItem[]>([])
  const [documentId, setDocumentId] = useState('')
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(5)
  const [sourceType, setSourceType] = useState('')
  const [loadingDocs, setLoadingDocs] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<AskResponse | null>(null)

  useEffect(() => {
    getDocuments()
      .then((items) => {
        setDocuments(items)
        const requested =
          params.get('document_id') ||
          localStorage.getItem(LAST_DOCUMENT_KEY) ||
          ''

        if (
          requested &&
          items.some((item) => String(item.document_id) === requested)
        ) {
          setDocumentId(requested)
        }
      })
      .catch((err) => {
        setError(
          err instanceof Error ? err.message : 'Unable to load documents.',
        )
      })
      .finally(() => setLoadingDocs(false))
  }, [params])

  function selectDocument(value: string) {
    setDocumentId(value)
    if (value) {
      localStorage.setItem(LAST_DOCUMENT_KEY, value)
    } else {
      localStorage.removeItem(LAST_DOCUMENT_KEY)
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      setResult(
        await askDocument({
          question: question.trim(),
          top_k: topK,
          source_type: sourceType || null,
          document_id: documentId ? Number(documentId) : null,
        }),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Question failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ask-layout">
      <section>
        <PageHeader
          eyebrow="Research assistant"
          title="Ask your documents"
          description="Get a grounded answer from the content ARIOS has indexed."
        />

        {loadingDocs ? (
          <LoadingState label="Loading documents…" />
        ) : (
          <form className="panel ask-form" onSubmit={submit}>
            <label htmlFor="document">Document</label>
            <select
              id="document"
              value={documentId}
              onChange={(event) => selectDocument(event.target.value)}
            >
              <option value="">All documents</option>
              {documents.map((document) => (
                <option key={document.document_id} value={document.document_id}>
                  #{document.document_id} — {document.title}
                </option>
              ))}
            </select>

            <label htmlFor="question">Question</label>
            <textarea
              id="question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              rows={5}
              placeholder="What are the main findings?"
              required
              autoFocus
            />

            <div className="form-grid">
              <div>
                <label htmlFor="top-k">Results to retrieve</label>
                <input
                  id="top-k"
                  type="number"
                  min="1"
                  max="50"
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                />
              </div>

              <div>
                <label htmlFor="source-type">
                  Source type <span className="optional">optional</span>
                </label>
                <input
                  id="source-type"
                  value={sourceType}
                  onChange={(event) => setSourceType(event.target.value)}
                  placeholder="e.g. web, pdf"
                />
              </div>
            </div>

            <SubmitButton
              idleLabel="Ask ARIOS"
              loadingLabel="Finding an answer…"
              loading={loading}
              disabled={!question.trim()}
            />
          </form>
        )}

        {error && <ErrorMessage message={error} />}
      </section>

      {result && <AnswerPanel result={result} />}
    </div>
  )
}
