interface SubmitButtonProps {
  idleLabel: string
  loadingLabel: string
  loading: boolean
  disabled?: boolean
}

export default function SubmitButton({
  idleLabel,
  loadingLabel,
  loading,
  disabled = false,
}: SubmitButtonProps) {
  return (
    <button className="button" type="submit" disabled={loading || disabled}>
      {loading && <span className="spinner small-spinner" />}
      {loading ? loadingLabel : idleLabel}
    </button>
  )
}
