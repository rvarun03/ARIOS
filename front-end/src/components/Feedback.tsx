export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" />
      {label}
    </div>
  )
}

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="error" role="alert">
      <strong>Something went wrong</strong>
      <span>{message}</span>
    </div>
  )
}
