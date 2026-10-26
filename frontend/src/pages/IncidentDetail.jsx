import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';

const SEVERITIES = ['critical', 'high', 'medium', 'low'];

export function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showZoneModal, setShowZoneModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [zoneForm, setZoneForm] = useState({
    incident_id: id || '',
    name: '',
    severity: 'medium',
    affected_population: 0,
    vulnerable_children: 0,
    vulnerable_elderly: 0,
    vulnerable_medical: 0,
    buildings_damaged: 0,
    buildings_destroyed: 0,
    infrastructure_damage: 0,
    assessment_notes: '',
  });

  useEffect(() => {
    if (id) loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [incidentData, zonesData] = await Promise.all([
        api.get(`/incidents/${id}`),
        api.get(`/incidents/${id}/zones`),
      ]);
      setIncident(incidentData);
      setZones(zonesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateZone = async (e) => {
    e.preventDefault();
    try {
      setCreating(true);
      await api.post(`/incidents/${id}/zones`, zoneForm);
      setShowZoneModal(false);
      setZoneForm({ incident_id: id || '', name: '', severity: 'medium', affected_population: 0, vulnerable_children: 0, vulnerable_elderly: 0, vulnerable_medical: 0, buildings_damaged: 0, buildings_destroyed: 0, infrastructure_damage: 0, assessment_notes: '' });
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create zone');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <LoadingScreen />;

  return (
    <div>
      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

      {incident && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
            <div>
              <Link to="/incidents" className="btn btn-secondary" style={{ marginBottom: 'var(--spacing-sm)', display: 'inline-flex' }}>
                ← Back to Incidents
              </Link>
              <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>{incident.name}</h1>
              <div style={{ display: 'flex', gap: 'var(--spacing-md)', flexWrap: 'wrap' }}>
                <span className={`badge badge-${incident.disaster_type}`}>{incident.disaster_type}</span>
                <span className={`badge badge-${incident.severity}`}>{incident.severity}</span>
                <span className={`badge badge-${incident.status}`}>{incident.status}</span>
              </div>
            </div>
            <button className="btn btn-primary" onClick={() => setShowZoneModal(true)}>
              <span>+</span> Add Zone
            </button>
          </div>

          <div className="grid grid-4" style={{ marginBottom: 'var(--spacing-lg)' }}>
            <div className="card">
              <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 'var(--spacing-xs)' }}>Location</p>
              <p style={{ fontSize: '18px', fontWeight: '600' }}>{incident.longitude?.toFixed(4)}, {incident.latitude?.toFixed(4)}</p>
            </div>
            <div className="card">
              <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 'var(--spacing-xs)' }}>Affected Population</p>
              <p style={{ fontSize: '18px', fontWeight: '600' }}>{incident.affected_population?.toLocaleString() ?? 0}</p>
            </div>
            <div className="card">
              <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 'var(--spacing-xs)' }}>Estimated Population</p>
              <p style={{ fontSize: '18px', fontWeight: '600' }}>{incident.estimated_affected_population?.toLocaleString() ?? 0}</p>
            </div>
            <div className="card">
              <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 'var(--spacing-xs)' }}>Reported By</p>
              <p style={{ fontSize: '18px', fontWeight: '600' }}>{incident.reported_by || 'Unknown'}</p>
            </div>
          </div>

          <div className="grid grid-2" style={{ marginBottom: 'var(--spacing-lg)' }}>
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Description</h2>
              </div>
              <p style={{ color: incident.description ? 'var(--color-text)' : 'var(--color-text-muted)' }}>
                {incident.description || 'No description provided'}
              </p>
            </div>
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Timeline</h2>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                <div><strong>Start:</strong> {new Date(incident.start_date).toLocaleString()}</div>
                <div><strong>Created:</strong> {new Date(incident.created_at).toLocaleString()}</div>
                <div><strong>Updated:</strong> {new Date(incident.updated_at).toLocaleString()}</div>
                {incident.end_date && <div><strong>End:</strong> {new Date(incident.end_date).toLocaleString()}</div>}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Affected Zones ({zones.length})</h2>
            </div>
            {zones.length ? (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Severity</th>
                      <th>Impact Score</th>
                      <th>Population</th>
                      <th>Vulnerable (C/E/M)</th>
                      <th>Buildings (Damaged/Destroyed)</th>
                      <th>Infrastructure Damage</th>
                      <th>Assessed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {zones.map((zone) => (
                      <tr key={zone.id}>
                        <td><strong>{zone.name}</strong></td>
                        <td><span className={`badge badge-${zone.severity}`}>{zone.severity}</span></td>
                        <td>{zone.impact_score?.toFixed(2) ?? 0}</td>
                        <td>{zone.affected_population?.toLocaleString() ?? 0}</td>
                        <td>{zone.vulnerable_children}/{zone.vulnerable_elderly}/{zone.vulnerable_medical}</td>
                        <td>{zone.buildings_damaged}/{zone.buildings_destroyed}</td>
                        <td>{(zone.infrastructure_damage * 100).toFixed(1)}%</td>
                        <td>{zone.assessment_timestamp ? new Date(zone.assessment_timestamp).toLocaleDateString() : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">🗺️</div>
                <p>No affected zones defined for this incident</p>
                <button className="btn btn-primary mt-sm" onClick={() => setShowZoneModal(true)}>Add First Zone</button>
              </div>
            )}
          </div>
        </>
      )}

      {showZoneModal && (
        <div className="modal-overlay" onClick={() => setShowZoneModal(false)}>
          <div className="modal" style={{ maxWidth: '700px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add Affected Zone</h2>
              <button className="modal-close" onClick={() => setShowZoneModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreateZone}>
              <div className="modal-body" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
                <div className="form-group">
                  <label className="form-label">Zone Name *</label>
                  <input type="text" className="form-input" required value={zoneForm.name} onChange={(e) => setZoneForm({ ...zoneForm, name: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Severity *</label>
                    <select className="form-select" value={zoneForm.severity} onChange={(e) => setZoneForm({ ...zoneForm, severity: e.target.value })}>
                      {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Affected Population</label>
                    <input type="number" className="form-input" value={zoneForm.affected_population} onChange={(e) => setZoneForm({ ...zoneForm, affected_population: parseInt(e.target.value) || 0 })} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Vulnerable Populations</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--spacing-md)' }}>
                    <div>
                      <label className="form-label" style={{ fontSize: '12px' }}>Children</label>
                      <input type="number" className="form-input" value={zoneForm.vulnerable_children} onChange={(e) => setZoneForm({ ...zoneForm, vulnerable_children: parseInt(e.target.value) || 0 })} />
                    </div>
                    <div>
                      <label className="form-label" style={{ fontSize: '12px' }}>Elderly</label>
                      <input type="number" className="form-input" value={zoneForm.vulnerable_elderly} onChange={(e) => setZoneForm({ ...zoneForm, vulnerable_elderly: parseInt(e.target.value) || 0 })} />
                    </div>
                    <div>
                      <label className="form-label" style={{ fontSize: '12px' }}>Medical</label>
                      <input type="number" className="form-input" value={zoneForm.vulnerable_medical} onChange={(e) => setZoneForm({ ...zoneForm, vulnerable_medical: parseInt(e.target.value) || 0 })} />
                    </div>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Building Damage</label>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                    <div>
                      <label className="form-label" style={{ fontSize: '12px' }}>Damaged</label>
                      <input type="number" className="form-input" value={zoneForm.buildings_damaged} onChange={(e) => setZoneForm({ ...zoneForm, buildings_damaged: parseInt(e.target.value) || 0 })} />
                    </div>
                    <div>
                      <label className="form-label" style={{ fontSize: '12px' }}>Destroyed</label>
                      <input type="number" className="form-input" value={zoneForm.buildings_destroyed} onChange={(e) => setZoneForm({ ...zoneForm, buildings_destroyed: parseInt(e.target.value) || 0 })} />
                    </div>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Infrastructure Damage (0-1)</label>
                  <input type="number" step="0.1" min="0" max="1" className="form-input" value={zoneForm.infrastructure_damage} onChange={(e) => setZoneForm({ ...zoneForm, infrastructure_damage: parseFloat(e.target.value) || 0 })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Assessment Notes</label>
                  <textarea className="form-input" rows={3} value={zoneForm.assessment_notes} onChange={(e) => setZoneForm({ ...zoneForm, assessment_notes: e.target.value })} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowZoneModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>{creating ? 'Creating...' : 'Add Zone'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
