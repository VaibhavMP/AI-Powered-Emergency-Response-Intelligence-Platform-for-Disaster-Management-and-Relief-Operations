import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { LoadingScreen } from '../components/LoadingScreen';

const ROLES = ['coordinator', 'rescuer', 'medical', 'logistics', 'driver', 'communications', 'volunteer', 'other'];

export function Personnel() {
  const [personnel, setPersonnel] = useState([]);
  const [depots, setDepots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    role: 'volunteer',
    skills: '',
    availability: true,
    depot_id: '',
    deployment_status: 'available',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [personnelData, depotsData] = await Promise.all([
        api.get('/personnel'),
        api.get('/depots'),
      ]);
      setPersonnel(personnelData);
      setDepots(depotsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load personnel');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setCreating(true);
      if (editing) {
        await api.patch(`/personnel/${editing.id}`, formData);
      } else {
        await api.post('/personnel', formData);
      }
      setShowModal(false);
      setEditing(null);
      setFormData({ name: '', email: '', phone: '', role: 'volunteer', skills: '', availability: true, depot_id: '', deployment_status: 'available' });
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save personnel');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this personnel record?')) return;
    try {
      await api.delete(`/personnel/${id}`);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete personnel');
    }
  };

  if (loading) return <LoadingScreen />;

  const roleColors = {
    coordinator: 'var(--color-primary)',
    rescuer: 'var(--color-high)',
    medical: 'var(--color-low)',
    logistics: 'var(--color-recovery)',
    driver: 'var(--color-medium)',
    communications: '#6f42c1',
    volunteer: '#6c757d',
    other: '#17a2b8',
  };

  return (
    <div>
      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Personnel & Field Teams</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Manage field personnel, volunteers, and team assignments</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setEditing(null); setFormData({ name: '', email: '', phone: '', role: 'volunteer', skills: '', availability: true, depot_id: '', deployment_status: 'available' }); setShowModal(true); }}>
          <span>+</span> Add Personnel
        </button>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Depot</th>
                <th>Availability</th>
                <th>Deployment</th>
                <th>Skills</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {personnel.map(p => (
                <tr key={p.id}>
                  <td><strong>{p.name}</strong></td>
                  <td>
                    <span className="badge" style={{ background: `${roleColors[p.role] || '#6c757d'}20`, color: roleColors[p.role] || '#6c757d' }}>
                      {p.role}
                    </span>
                  </td>
                  <td>{p.email || '—'}</td>
                  <td>{p.phone || '—'}</td>
                  <td>{depots.find(d => d.id === p.depot_id)?.name || 'Unassigned'}</td>
                  <td><span className={`badge ${p.availability ? 'badge-low' : 'badge-cancelled'}`}>{p.availability ? 'Available' : 'Unavailable'}</span></td>
                  <td><span className={`badge badge-${p.deployment_status === 'deployed' ? 'in_progress' : p.deployment_status === 'available' ? 'low' : 'pending'}`}>{p.deployment_status}</span></td>
                  <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.skills || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                      <button className="btn btn-sm btn-secondary" onClick={() => { setEditing(p); setFormData(p); setShowModal(true); }}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(p.id)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
              {!personnel.length && <tr><td colSpan={9} className="text-center text-muted">No personnel records</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => { setShowModal(false); setEditing(null); }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{editing ? 'Edit Personnel' : 'Add Personnel'}</h2>
              <button className="modal-close" onClick={() => { setShowModal(false); setEditing(null); }}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Full Name *</label>
                  <input type="text" className="form-input" required value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Email</label>
                    <input type="email" className="form-input" value={formData.email || ''} onChange={e => setFormData({ ...formData, email: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Phone</label>
                    <input type="text" className="form-input" value={formData.phone || ''} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Role *</label>
                  <select className="form-select" value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value })}>
                    {ROLES.map(r => <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Skills</label>
                  <textarea className="form-input" rows={2} value={formData.skills} onChange={e => setFormData({ ...formData, skills: e.target.value })} placeholder="Comma-separated skills (e.g., First Aid, Navigation, Heavy Machinery)" />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Depot</label>
                    <select className="form-select" value={formData.depot_id} onChange={e => setFormData({ ...formData, depot_id: e.target.value })}>
                      <option value="">Unassigned</option>
                      {depots.filter(d => d.is_active).map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Deployment Status</label>
                    <select className="form-select" value={formData.deployment_status} onChange={e => setFormData({ ...formData, deployment_status: e.target.value })}>
                      <option value="available">Available</option>
                      <option value="deployed">Deployed</option>
                      <option value="standby">Standby</option>
                      <option value="resting">Resting</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                    <input type="checkbox" checked={formData.availability} onChange={e => setFormData({ ...formData, availability: e.target.checked })} />
                    Available for Deployment
                  </label>
                </div>
                <div className="form-group">
                  <label className="form-label">Certifications</label>
                  <textarea className="form-input" rows={2} value={formData.certifications || ''} onChange={e => setFormData({ ...formData, certifications: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Emergency Contact</label>
                    <input type="text" className="form-input" value={formData.emergency_contact || ''} onChange={e => setFormData({ ...formData, emergency_contact: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Emergency Phone</label>
                    <input type="text" className="form-input" value={formData.emergency_phone || ''} onChange={e => setFormData({ ...formData, emergency_phone: e.target.value })} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => { setShowModal(false); setEditing(null); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>{creating ? 'Saving...' : (editing ? 'Update' : 'Create')}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}