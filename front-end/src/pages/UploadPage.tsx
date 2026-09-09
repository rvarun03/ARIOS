import { useState } from 'react'
import type { FormEvent } from 'react'
import { ErrorMessage } from '../components/Feedback'
import PageHeader from '../components/PageHeader'
import PipelineResult from '../components/PipelineResult'
import SubmitButton from '../components/SubmitButton'
import { uploadDocument } from '../lib/api'
import type { UploadResponse } from '../types/api'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<UploadResponse | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      setResult(await uploadDocument(file))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  const fileDescription = file
    ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
    : 'Click to browse your files'

  return (
    <div className="narrow">
      <PageHeader
        eyebrow="Add knowledge"
        title="Upload a document"
        description="Upload a PDF or image for extraction, analysis, and indexing."
      />

      <form className="panel" onSubmit={submit}>
        <label className="file-drop" htmlFor="document-file">
          <span className="upload-icon">↑</span>
          <strong>{file?.name || 'Choose a PDF or image'}</strong>
          <span>{fileDescription}</span>
        </label>
        <input
          className="sr-only"
          id="document-file"
          type="file"
          accept="application/pdf,image/*"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />

        <SubmitButton
          idleLabel="Upload and index"
          loadingLabel="Uploading and analyzing…"
          loading={loading}
          disabled={!file}
        />
      </form>

      {error && <ErrorMessage message={error} />}
      {result && <PipelineResult result={result} />}
    </div>
  )
}
