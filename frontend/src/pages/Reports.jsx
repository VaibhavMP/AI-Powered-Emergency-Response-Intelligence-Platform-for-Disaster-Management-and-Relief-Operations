import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { api } from '../api/client';

export function Reports() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => { loadAnalytics(); }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.get('/analytics/summary');
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
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
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Reports & Analytics</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Response performance and resource utilization insights</p>
        </div>
      </div>
      {analytics ? (
        <div className="grid grid-2">
          <div className="card">
            <div className="card-header"><h2 className="card-title">Overview</h2></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Total Incidents:</span><strong>{analytics.total_incidents}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Total Resources Allocated:</span><strong>{analytics.total_resources_allocated?.toLocaleString()}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Total Resources Delivered:</span><strong>{analytics.total_resources_delivered?.toLocaleString()}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>People Affected:</span><strong>{analytics.total_people_affected?.toLocaleString()}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>People Assisted:</span><strong>{analytics.total_people_assisted?.toLocaleString()}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Avg Response Time (hrs):</span><strong>{analytics.average_response_time_hours ?? 'N/A'}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Mission Completion Rate:</span><strong>{analytics.mission_completion_rate ? (analytics.mission_completion_rate * 100).toFixed(1) + '%' : 'N/A'}</strong></div>
            </div>
          </div>
          <div className="card">
            <div className="card-header"><h2 className="card-title">Unmet Demand by Type</h2></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
              {analytics.unmet_demand_by_type && Object.entries(analytics.unmet_demand_by_type).map(([type, qty]) => (
                <div key={type} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>{type.replace('_', ' ')}:</span>
                  <strong>{Number(qty).toLocaleString()}</strong>
                </div>
              ))}
              {!analytics.unmet_demand_by_type || Object.keys(analytics.unmet_demand_by_type).length === 0 && (
                <p className="text-muted">No unmet demand recorded</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state"><p>No analytics data available</p></div>
      )}
    </div>
  );
}
