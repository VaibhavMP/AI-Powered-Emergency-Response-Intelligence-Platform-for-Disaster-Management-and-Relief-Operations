import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { LoadingScreen } from '../components/LoadingScreen';

export function Dashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
        const [summaryData, activityData] = await Promise.all([
          api.get('/dashboard/summary'),
          api.get('/dashboard/activity?limit=10'),
        ]);
      setSummary(summaryData);
      setActivity(activityData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingScreen />;

  const statCards = [
    { label: 'Active Incidents', value: summary?.total_active_incidents ?? 0, icon: '🚨', color: 'var(--color-primary)' },
    { label: 'Critical Incidents', value: summary?.critical_incidents ?? 0, icon: '⚠️', color: 'var(--color-critical)' },
    { label: 'Resources Available', value: summary?.resources_available ?? 0, icon: '📦', color: 'var(--color-low)' },
    { label: 'Resources Deployed', value: summary?.resources_deployed ?? 0, icon: '🚚', color: 'var(--color-medium)' },
    { label: 'Active Personnel', value: summary?.active_personnel ?? 0, icon: '👥', color: 'var(--color-recovery)' },
    { label: 'People Affected', value: summary?.people_affected ?? 0, icon: '👤', color: 'var(--color-high)' },
    { label: 'People Assisted', value: summary?.people_assisted ?? 0, icon: '✅', color: 'var(--color-low)' },
    { label: 'High Incidents', value: summary?.high_incidents ?? 0, icon: '🔴', color: 'var(--color-high)' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Dashboard</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Real-time overview of disaster response operations</p>
        </div>
        <button className="btn btn-primary" onClick={loadDashboard}>
          <span>⟳</span> Refresh
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid grid-4" style={{ marginBottom: 'var(--spacing-lg)' }}>
        {statCards.map((stat, i) => (
          <div key={i} className="card" style={{ borderLeft: `4px solid ${stat.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 'var(--spacing-xs)' }}>{stat.label}</p>
                <p style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-text)' }}>{stat.value.toLocaleString()}</p>
              </div>
              <div style={{ fontSize: '32px', opacity: 0.8 }}>{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-2" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Incidents</h2>
            <Link to="/incidents" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Population</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {activity?.recent_incidents?.slice(0, 5).map((inc) => (
                  <tr key={inc.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/incidents/${inc.id}`)}>
                    <td><strong>{inc.name}</strong></td>
                    <td>{inc.disaster_type}</td>
                    <td><span className={`badge badge-${inc.severity}`}>{inc.severity}</span></td>
                    <td><span className={`badge badge-${inc.status}`}>{inc.status}</span></td>
                    <td>{inc.affected_population?.toLocaleString() ?? 0}</td>
                    <td>{new Date(inc.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {!activity?.recent_incidents?.length && (
                  <tr><td colSpan={6} className="text-center text-muted">No incidents found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Missions</h2>
            <Link to="/missions" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Mission</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Departure</th>
                  <th>Destination</th>
                </tr>
              </thead>
              <tbody>
                {activity?.recent_missions?.slice(0, 5).map((mission) => (
                  <tr key={mission.id}>
                    <td><strong>{mission.name}</strong></td>
                    <td><span className={`badge badge-${mission.status}`}>{mission.status}</span></td>
                    <td>{mission.priority}</td>
                    <td>{mission.departure_time ? new Date(mission.departure_time).toLocaleString() : 'Not set'}</td>
                    <td>{mission.destination_depot_id ? 'Depot' : 'Zone'}</td>
                  </tr>
                ))}
                {!activity?.recent_missions?.length && (
                  <tr><td colSpan={5} className="text-center text-muted">No missions found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">High Priority Alerts</h2>
          </div>
          {activity?.high_priority_alerts?.length ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
              {activity.high_priority_alerts.map((alert, i) => (
                <div key={i} className="alert alert-error" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{alert.incident_name}</strong>
                    <p style={{ fontSize: '12px', marginTop: 'var(--spacing-xs)' }}>{alert.message}</p>
                  </div>
                  <span className="badge badge-critical">{alert.severity}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">✓</div>
              <p>No critical alerts at this time</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Quick Actions</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-sm)' }}>
            <Link to="/incidents" className="btn btn-secondary" style={{ justifyContent: 'flex-start', padding: 'var(--spacing-md)' }}>
              <span style={{ fontSize: '20px' }}>🚨</span>
              <div>
                <div style={{ fontWeight: '500' }}>New Incident</div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Report a disaster</div>
              </div>
            </Link>
            <Link to="/resources" className="btn btn-secondary" style={{ justifyContent: 'flex-start', padding: 'var(--spacing-md)' }}>
              <span style={{ fontSize: '20px' }}>📦</span>
              <div>
                <div style={{ fontWeight: '500' }}>Manage Resources</div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Update inventory</div>
              </div>
            </Link>
            <Link to="/missions" className="btn btn-secondary" style={{ justifyContent: 'flex-start', padding: 'var(--spacing-md)' }}>
              <span style={{ fontSize: '20px' }}>🚁</span>
              <div>
                <div style={{ fontWeight: '500' }}>Create Mission</div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Deploy field team</div>
              </div>
            </Link>
            <Link to="/predictions" className="btn btn-secondary" style={{ justifyContent: 'flex-start', padding: 'var(--spacing-md)' }}>
              <span style={{ fontSize: '20px' }}>📈</span>
              <div>
                <div style={{ fontWeight: '500' }}>Run Prediction</div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Estimate demand</div>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}