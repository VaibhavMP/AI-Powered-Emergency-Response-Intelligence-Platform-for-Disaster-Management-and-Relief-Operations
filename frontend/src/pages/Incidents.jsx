import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';

const DISASTER_TYPES = ['flood', 'earthquake', 'cyclone', 'wildfire', 'drought', 'landslide', 'tsunami', 'volcano', 'other'];
const STATUSES = ['active', 'monitoring', 'contained', 'recovered', 'closed'];
const SEVERITIES = ['critical', 'high', 'medium', 'low', 'recovery'];

export function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    disaster_type: '',
    severity: '',
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    disaster_type: 'flood',
    severity: 'medium',
    description: '',
    longitude: 0,
    latitude: 0,
    affected_population: 0,
    estimated_affected_population: 0,
  });

  const navigate = useNavigate();

  useEffect(() => {
    loadIncidents();
  }, [page, filters]);

  const loadIncidents = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: page.toString(), page_size: pageSize.toString() });
      if (filters.search) params.append('search', filters.search);
      if (filters.status) params.append('status', filters.status);
      if (filters.disaster_type) params.append('disaster_type', filters.disaster_type);
      if (filters.severity) params.append('severity', filters.severity);

      const data = await api.get(`/incidents?${params}`);
      setIncidents(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      setCreating(true);
      const newIncident = await api.post('/incidents', formData);
      setShowCreateModal(false);
      setFormData({ name: '', disaster_type: 'flood', severity: 'medium', description: '', longitude: 0, latitude: 0, affected_population: 0, estimated_affected_population: 0 });
      loadIncidents();
      navigate(`/incidents/${newIncident.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create incident');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this incident?')) return;
    try {
      await api.delete(`/incidents/${id}`);
      loadIncidents();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete incident');
    }
  };

  if (loading && !incidents.length) return <LoadingScreen />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Incidents</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Manage disaster incidents and track their status</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          <span>+</span> New Incident
        </button>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

      <div className="card" style={{ marginBottom: 'var(--spacing-md)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-md)', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: '200px' }}>
            <label className="form-label">Search</label>
            <input
              type="text"
              className="form-input"
              placeholder="Search incidents..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <div style={{ minWidth: '150px' }}>
            <label className="form-label">Status</label>
            <select className="form-select" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
              <option value="">All Statuses</option>
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div style={{ minWidth: '150px' }}>
            <label className="form-label">Disaster Type</label>
            <select className="form-select" value={filters.disaster_type} onChange={(e) => setFilters({ ...filters, disaster_type: e.target.value })}>
              <option value="">All Types</option>
              {DISASTER_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div style={{ minWidth: '150px' }}>
            <label className="form-label">Severity</label>
            <select className="form-select" value={filters.severity} onChange={(e) => setFilters({ ...filters, severity: e.target.value })}>
              <option value="">All Severities</option>
              {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Location</th>
                <th>Population</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((inc) => (
                <tr key={inc.id}>
                  <td><strong>{inc.name}</strong></td>
                  <td>{inc.disaster_type}</td>
                  <td><span className={`badge badge-${inc.severity}`}>{inc.severity}</span></td>
                  <td><span className={`badge badge-${inc.status}`}>{inc.status}</span></td>
                  <td>{inc.longitude?.toFixed(4)}, {inc.latitude?.toFixed(4)}</td>
                  <td>{inc.affected_population?.toLocaleString() ?? 0}</td>
                  <td>{new Date(inc.created_at).toLocaleDateString()}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                      <Link to={`/incidents/${inc.id}`} className="btn btn-sm btn-secondary">View</Link>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(inc.id)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
              {!incidents.length && (
                <tr><td colSpan={8} className="text-center text-muted" style={{ padding: 'var(--spacing-xl)' }}>No incidents found</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {total > pageSize && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--spacing-md)', borderTop: '1px solid var(--color-border)' }}>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>
              Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} incidents
            </p>
            <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
              <button className="btn btn-sm btn-secondary" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</button>
              <button className="btn btn-sm btn-secondary" onClick={() => setPage(p => Math.min(Math.ceil(total / pageSize), p + 1))} disabled={page >= Math.ceil(total / pageSize)}>Next</button>
            </div>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create New Incident</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Incident Name *</label>
                  <input type="text" className="form-input" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Disaster Type *</label>
                    <select className="form-select" value={formData.disaster_type} onChange={(e) => setFormData({ ...formData, disaster_type: e.target.value })}>
                      {DISASTER_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Severity *</label>
                    <select className="form-select" value={formData.severity} onChange={(e) => setFormData({ ...formData, severity: e.target.value })}>
                      {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Longitude *</label>
                    <input type="number" step="any" className="form-input" required value={formData.longitude} onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Latitude *</label>
                    <input type="number" step="any" className="form-input" required value={formData.latitude} onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea className="form-input" rows={3} value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Affected Population</label>
                    <input type="number" className="form-input" value={formData.affected_population} onChange={(e) => setFormData({ ...formData, affected_population: parseInt(e.target.value) || 0 })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Estimated Affected Population</label>
                    <input type="number" className="form-input" value={formData.estimated_affected_population} onChange={(e) => setFormData({ ...formData, estimated_affected_population: parseInt(e.target.value) || 0 })} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>{creating ? 'Creating...' : 'Create Incident'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
