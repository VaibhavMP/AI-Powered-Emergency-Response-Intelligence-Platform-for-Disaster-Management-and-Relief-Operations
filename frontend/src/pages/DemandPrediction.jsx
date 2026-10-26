import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { api } from '../api/client';

const RESOURCE_TYPES = ['food_packets', 'water', 'medical_kits', 'shelter', 'rescue_vehicles', 'personnel', 'fuel', 'generators', 'communication', 'other'];

export function DemandPrediction() {
  const [incidents, setIncidents] = useState([]);
  const [zones, setZones] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState('');
  const [selectedZones, setSelectedZones] = useState([]);
  const [vulnerabilityAdjustment, setVulnerabilityAdjustment] = useState(1.0);

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
      loadZones();
      loadPredictions();
    }
  }, [selectedIncident]);

  const loadZones = async () => {
    try {
      const data = await api.get(`/incidents/${selectedIncident}/zones`);
      setZones(data);
      setSelectedZones(data.map(z => z.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load zones');
    }
  };

  const loadPredictions = async () => {
    try {
      const data = await api.get(`/predictions`);
      const incidentZones = zones.map(z => z.id);
      setPredictions(data.filter(p => incidentZones.includes(p.zone_id)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load predictions');
    }
  };

  const runPrediction = async () => {
    if (!selectedIncident) return;
    try {
      setPredicting(true);
      setError(null);
      const request = {
        incident_id: selectedIncident,
        zone_ids: selectedZones.length > 0 ? selectedZones : undefined,
        vulnerability_adjustment: vulnerabilityAdjustment,
      };
      const newPredictions = await api.post('/predictions/predict', request);
      setPredictions(prev => [...newPredictions, ...prev.filter(p => !newPredictions.some(np => np.zone_id === p.zone_id && np.resource_type === p.resource_type))]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
    } finally {
      setPredicting(false);
    }
  };

  const getResourceColor = (type) => {
    const colors = {
      food_packets: '#28a745',
      water: '#17a2b8',
      medical_kits: '#dc3545',
      shelter: '#fd7e14',
      rescue_vehicles: '#6f42c1',
      personnel: '#20c997',
    };
    return colors[type] || '#6c757d';
  };

  if (loading && !incidents.length) return <LoadingScreen />;

  const groupedPredictions = predictions.reduce((acc, p) => {
    if (!acc[p.zone_id]) acc[p.zone_id] = {};
    acc[p.zone_id][p.resource_type] = p;
    return acc;
  }, {});

  return (
    <div>
      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Demand Prediction</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Estimate resource demand for affected zones based on population, severity, and vulnerability</p>
        </div>
        <button className="btn btn-primary" onClick={runPrediction} disabled={predicting || !selectedIncident || selectedZones.length === 0}>
          {predicting ? 'Predicting...' : 'Run Prediction'}
        </button>
      </div>

      <div className="grid grid-3" style={{ marginBottom: 'var(--spacing-lg)' }}>
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
            <label className="form-label">Vulnerability Adjustment</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={vulnerabilityAdjustment}
                onChange={e => setVulnerabilityAdjustment(parseFloat(e.target.value))}
                style={{ flex: 1 }}
              />
              <span style={{ fontWeight: '600', minWidth: '50px' }}>{vulnerabilityAdjustment.toFixed(1)}x</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>
              Adjust demand based on vulnerable populations (children, elderly, medical)
            </p>
          </div>
        </div>
        <div className="card">
          <div className="form-group">
            <label className="form-label">Affected Zones ({selectedZones.length}/{zones.length})</label>
            <div style={{ maxHeight: '100px', overflowY: 'auto', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: 'var(--spacing-sm)' }}>
              {zones.map(zone => (
                <label key={zone.id} style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', padding: 'var(--spacing-xs) 0', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={selectedZones.includes(zone.id)}
                    onChange={e => e.target.checked
                      ? setSelectedZones([...selectedZones, zone.id])
                      : setSelectedZones(selectedZones.filter(z => z !== zone.id))
                    }
                  />
                  <span style={{ fontSize: '13px' }}>{zone.name} ({zone.severity}) - {zone.affected_population?.toLocaleString()} people</span>
                </label>
              ))}
              {!zones.length && <span className="text-muted">No zones defined for this incident</span>}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Predicted Demand by Zone & Resource</h2>
          <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
            Method: Baseline Regression v1 | Adjustment: {vulnerabilityAdjustment.toFixed(1)}x
          </div>
        </div>

        {predictions.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Severity</th>
                  <th>Population</th>
                  {RESOURCE_TYPES.map(rt => (
                    <th key={rt} style={{ textAlign: 'center' }}>
                      <span style={{ display: 'inline-block', width: 12, height: 12, borderRadius: '50%', background: getResourceColor(rt), marginRight: 'var(--spacing-xs)' }}></span>
                      {rt.replace('_', ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {zones.map(zone => {
                  const zonePredictions = groupedPredictions[zone.id] || {};
                  return (
                    <tr key={zone.id}>
                      <td><strong>{zone.name}</strong></td>
                      <td><span className={`badge badge-${zone.severity}`}>{zone.severity}</span></td>
                      <td>{zone.affected_population?.toLocaleString() ?? 0}</td>
                      {RESOURCE_TYPES.map(rt => {
                        const pred = zonePredictions[rt];
                        return (
                          <td key={rt} style={{ textAlign: 'center' }}>
                            {pred ? (
                              <div>
                                <strong>{pred.predicted_quantity.toLocaleString()}</strong>
                                <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                                  {pred.lower_bound?.toLocaleString()}–{pred.upper_bound?.toLocaleString()}
                                </div>
                              </div>
                            ) : (
                              <span className="text-muted">—</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state" style={{ padding: 'var(--spacing-xl)' }}>
            <div className="empty-state-icon">📈</div>
            <p>No predictions generated yet</p>
            <p style={{ fontSize: '13px', marginTop: 'var(--spacing-xs)' }}>Select an incident, choose zones, and click "Run Prediction"</p>
          </div>
        )}

        {predictions.length > 0 && (
          <div style={{ marginTop: 'var(--spacing-lg)', paddingTop: 'var(--spacing-lg)', borderTop: '1px solid var(--color-border)' }}>
            <h3 style={{ marginBottom: 'var(--spacing-md)' }}>Prediction Details</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Zone</th>
                    <th>Resource</th>
                    <th>Predicted</th>
                    <th>Range</th>
                    <th>Confidence</th>
                    <th>Method</th>
                    <th>Vuln. Adj.</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.slice().sort((a, b) => new Date(b.prediction_timestamp).getTime() - new Date(a.prediction_timestamp).getTime()).map(pred => (
                    <tr key={pred.id}>
                      <td>{zones.find(z => z.id === pred.zone_id)?.name || pred.zone_id.slice(0, 8)}</td>
                      <td>{pred.resource_type.replace('_', ' ')}</td>
                      <td>{pred.predicted_quantity.toLocaleString()}</td>
                      <td>{pred.lower_bound?.toLocaleString()}–{pred.upper_bound?.toLocaleString()}</td>
                      <td>{pred.confidence_level ? (pred.confidence_level * 100).toFixed(0) + '%' : 'N/A'}</td>
                      <td>{pred.method}</td>
                      <td>{pred.vulnerability_adjustment.toFixed(1)}x</td>
                      <td>{new Date(pred.prediction_timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
