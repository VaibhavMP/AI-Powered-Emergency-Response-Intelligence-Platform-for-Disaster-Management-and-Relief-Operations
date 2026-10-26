import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { api } from '../api/client';

const RESOURCE_TYPES = ['food_packets', 'water', 'medical_kits', 'shelter', 'rescue_vehicles', 'personnel', 'fuel', 'generators', 'communication', 'other'];

export function Allocations() {
  const [incidents, setIncidents] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState('');
  const [priorityOverrides, setPriorityOverrides] = useState({});

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    try {
      const data = await api.get('/incidents?page_size=50&status=active');
      setIncidents(data.items);
      if (data.items.length > 0 && !selectedIncident) {
        setSelectedIncident(data.items[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedIncident) {
      loadAllocations();
      loadInventory();
    }
  }, [selectedIncident]);

  const loadAllocations = async () => {
    try {
      const data = await api.get(`/allocations`);
      const incidentZones = incidents.find(i => i.id === selectedIncident)?.id;
      // Filter by zones of selected incident - simplified for now
      setAllocations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load allocations');
    }
  };

  const loadInventory = async () => {
    try {
      const data = await api.get('/resources');
      setInventory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load inventory');
    }
  };

  const runOptimization = async () => {
    if (!selectedIncident) return;
    try {
      setOptimizing(true);
      setError(null);
      const request = {
        incident_id: selectedIncident,
        priority_overrides: priorityOverrides,
      };
      const result = await api.post('/allocations/optimize', request);
      setOptimizationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Optimization failed');
    } finally {
      setOptimizing(false);
    }
  };

  const handleApprove = async (allocationId) => {
    try {
      await api.post(`/allocations/${allocationId}/approve`);
      loadAllocations();
      if (optimizationResult) {
        setOptimizationResult({
          ...optimizationResult,
          recommendations: optimizationResult.recommendations.map(a =>
            a.id === allocationId ? { ...a, approved: true, status: 'approved' } : a
          ),
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve allocation');
    }
  };

  if (loading) return <LoadingScreen />;

  return (
    <div>
      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Resource Allocation</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Optimize resource distribution across affected zones</p>
        </div>
        <button className="btn btn-primary" onClick={runOptimization} disabled={optimizing || !selectedIncident}>
          {optimizing ? 'Optimizing...' : 'Run Optimization'}
        </button>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <div className="card">
          <div className="form-group">
            <label className="form-label">Select Incident</label>
            <select className="form-select" value={selectedIncident} onChange={e => setSelectedIncident(e.target.value)}>
              <option value="">Select an incident</option>
              {incidents.map(inc => <option key={inc.id} value={inc.id}>{inc.name} ({inc.disaster_type})</option>)}
            </select>
          </div>
        </div>
        <div className="card">
          <div className="form-group">
            <label className="form-label">Priority Overrides</label>
            <div style={{ display: 'flex', gap: 'var(--spacing-md)', flexWrap: 'wrap' }}>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
              Zone priorities are based on severity. Use API to set manual overrides.
            </p>
          </div>
        </div>
      </div>

      {optimizationResult && (
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)', borderLeft: '4px solid var(--color-low)' }}>
          <div className="card-header">
            <h2 className="card-title">Optimization Results</h2>
            <span className="badge badge-low">{optimizationResult.optimization_status}</span>
          </div>
          {optimizationResult.message && <p style={{ marginBottom: 'var(--spacing-md)', color: 'var(--color-text-muted)' }}>{optimizationResult.message}</p>}

          <div className="grid grid-2" style={{ marginBottom: 'var(--spacing-md)' }}>
            <div>
              <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Coverage Summary</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 'var(--spacing-sm)' }}>
                {Object.entries(optimizationResult.coverage_summary).map(([zoneId, cov]) => (
                  <div key={zoneId} className="card" style={{ padding: 'var(--spacing-sm)' }}>
                    <strong>{cov.zone_name}</strong>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                      {cov.coverage_pct}% covered ({cov.total_allocated}/{cov.total_demand})
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Unmet Demand</h4>
              {optimizationResult.unmet_demand.length > 0 ? (
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {optimizationResult.unmet_demand.map((d, i) => (
                    <div key={i} style={{ padding: 'var(--spacing-xs) 0', borderBottom: '1px solid var(--color-border)', fontSize: '13px' }}>
                      <strong>{d.zone_name}</strong> - {d.resource_type}: {d.unmet.toLocaleString()} unmet
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">All demand met!</p>
              )}
            </div>
          </div>

          <h4 style={{ marginBottom: 'var(--spacing-sm)', marginTop: 'var(--spacing-lg)' }}>Recommended Allocations</h4>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Resource</th>
                  <th>Allocated</th>
                  <th>Source Depot</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {optimizationResult.recommendations.map(alloc => (
                  <tr key={alloc.id}>
                    <td>{alloc.zone_id.slice(0, 8)}</td>
                    <td>{alloc.resource_type.replace('_', ' ')}</td>
                    <td>{alloc.allocated_quantity.toLocaleString()}</td>
                    <td>{alloc.source_depot_id?.slice(0, 8) || '—'}</td>
                    <td>{alloc.priority}</td>
                    <td><span className={`badge badge-${alloc.status === 'approved' ? 'low' : 'pending'}`}>{alloc.status}</span></td>
                    <td>
                      {!alloc.approved && (
                        <button className="btn btn-sm btn-primary" onClick={() => handleApprove(alloc.id)}>Approve</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Current Allocations</h2>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Zone</th>
                <th>Resource</th>
                <th>Allocated</th>
                <th>Fulfilled</th>
                <th>Source Depot</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Approved</th>
              </tr>
            </thead>
            <tbody>
              {allocations.map(alloc => (
                <tr key={alloc.id}>
                  <td>{alloc.zone_id.slice(0, 8)}</td>
                  <td>{alloc.resource_type.replace('_', ' ')}</td>
                  <td>{alloc.allocated_quantity.toLocaleString()}</td>
                  <td>{alloc.fulfilled_quantity.toLocaleString()}</td>
                  <td>{alloc.source_depot_id?.slice(0, 8) || '—'}</td>
                  <td>{alloc.priority}</td>
                  <td><span className={`badge badge-${alloc.status === 'approved' ? 'low' : 'pending'}`}>{alloc.status}</span></td>
                  <td>{alloc.approved ? '✓' : '✗'}</td>
                </tr>
              ))}
              {!allocations.length && <tr><td colSpan={8} className="text-center text-muted">No allocations recorded</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
