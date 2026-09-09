import { useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorMessage } from '../components/Feedback'
import PageHeader from '../components/PageHeader'
import PipelineResult from '../components/PipelineResult'
import SubmitButton from '../components/SubmitButton'
import { ingestSource } from '../lib/api'
import type { IngestResponse } from '../types/api'

export default function IngestPage() {
  const [source, setSource] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<IngestResponse | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      setResult(await ingestSource(source.trim()))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingestion failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="narrow">
      <PageHeader
        eyebrow="Add knowledge"
        title="Ingest a source"
        description="Enter a public URL or a source path. ARIOS will detect, analyze, save, and index it."
      />

      <form className="panel" onSubmit={submit}>
        <label htmlFor="source">Source URL or path</label>
        <input
          id="source"
          type="text"
          value={source}
          onChange={(event) => setSource(event.target.value)}
          placeholder="https://example.com/research-paper"
          required
          autoFocus
        />
        <p className="hint">
          Web pages and backend-supported local sources are accepted.
        </p>

        <SubmitButton
          idleLabel="Ingest and index"
          loadingLabel="Processing…"
          loading={loading}
          disabled={!source.trim()}
        />
      </form>

      {error && <ErrorMessage message={error} />}
      {result && <PipelineResult result={result} />}
    </div>
  )
}
