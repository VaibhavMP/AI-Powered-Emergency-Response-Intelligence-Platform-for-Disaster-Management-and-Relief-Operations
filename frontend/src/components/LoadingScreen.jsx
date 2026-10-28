export function LoadingScreen({ message = 'Loading telemetry data...' }) {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <p style={{ marginTop: 'var(--spacing-md)', color: 'var(--color-text-muted)', fontSize: '13px', letterSpacing: '0.5px' }}>
        {message}
      </p>
    </div>
  );
}
