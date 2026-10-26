import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { api } from '../api/client';

export function Settings() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadSources(); }, []);

  const loadSources = async () => {
    try {
      setLoading(true);
      const data = await api.get('/data-sources');
      setSources(data.items || data);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingScreen />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Settings</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Configure data sources and system preferences</p>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h2 className="card-title">Data Sources</h2></div>
        <div className="table-container">
          <table>
            <thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Last Sync</th><th>Enabled</th></tr></thead>
            <tbody>
              {sources.map(s => (
                <tr key={s.id}>
                  <td><strong>{s.name}</strong></td>
                  <td>{s.type}</td>
                  <td><span className={`badge badge-${s.status === 'active' ? 'low' : 'medium'}`}>{s.status}</span></td>
                  <td>{s.last_sync ? new Date(s.last_sync).toLocaleString() : 'Never'}</td>
                  <td>{s.enabled ? '✓' : '✗'}</td>
                </tr>
              ))}
              {!sources.length && <tr><td colSpan={5} className="text-center text-muted">No data sources configured</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
