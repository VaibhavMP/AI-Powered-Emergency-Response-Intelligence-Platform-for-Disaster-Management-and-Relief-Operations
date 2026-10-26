import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { api } from '../api/client';

export function Missions() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => { loadMissions(); }, []);

  const loadMissions = async () => {
    try {
      setLoading(true);
      const data = await api.get('/missions?page_size=50');
      setMissions(data.items || data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load missions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingScreen />;

  return (
    <div>
      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Missions</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Manage field missions and supply deliveries</p>
        </div>
      </div>
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Name</th><th>Status</th><th>Priority</th><th>Departure</th><th>Created</th></tr>
            </thead>
            <tbody>
              {missions.map(m => (
                <tr key={m.id}>
                  <td><strong>{m.name}</strong></td>
                  <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                  <td>{m.priority}</td>
                  <td>{m.departure_time ? new Date(m.departure_time).toLocaleString() : 'Not set'}</td>
                  <td>{new Date(m.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {!missions.length && <tr><td colSpan={5} className="text-center text-muted">No missions found</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
