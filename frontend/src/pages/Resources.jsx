import { useState, useEffect } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { api } from '../api/client';

const RESOURCE_TYPES = ['food_packets', 'water', 'medical_kits', 'shelter', 'rescue_vehicles', 'personnel', 'fuel', 'generators', 'communication', 'other'];

export function Resources() {
  const [depots, setDepots] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('depots');
  const [showDepotModal, setShowDepotModal] = useState(false);
  const [showInventoryModal, setShowInventoryModal] = useState(false);
  const [editingDepot, setEditingDepot] = useState(null);
  const [editingInventory, setEditingInventory] = useState(null);
  const [creating, setCreating] = useState(false);
  const [depotForm, setDepotForm] = useState({ name: '', longitude: 0, latitude: 0, capacity: 0 });
  const [inventoryForm, setInventoryForm] = useState({ depot_id: '', resource_type: 'food_packets', quantity: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [depotsData, inventoryData, movementsData] = await Promise.all([
        api.get('/depots'),
        api.get('/resources'),
        api.get('/resources/movements?limit=50'),
      ]);
      setDepots(depotsData);
      setInventory(inventoryData);
      setMovements(movementsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const handleDepotSubmit = async (e) => {
    e.preventDefault();
    try {
      setCreating(true);
      if (editingDepot) {
        await api.patch(`/depots/${editingDepot.id}`, depotForm);
      } else {
        await api.post('/depots', depotForm);
      }
      setShowDepotModal(false);
      setEditingDepot(null);
      setDepotForm({ name: '', longitude: 0, latitude: 0, capacity: 0 });
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save depot');
    } finally {
      setCreating(false);
    }
  };

  const handleInventorySubmit = async (e) => {
    e.preventDefault();
    try {
      setCreating(true);
      if (editingInventory) {
        await api.patch(`/resources/${editingInventory.id}`, inventoryForm);
      } else {
        await api.post('/resources', inventoryForm);
      }
      setShowInventoryModal(false);
      setEditingInventory(null);
      setInventoryForm({ depot_id: '', resource_type: 'food_packets', quantity: 0 });
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save inventory');
    } finally {
      setCreating(false);
    }
  };

  const handleDispatch = async (item) => {
    const qty = parseInt(window.prompt(`Dispatch quantity (available: ${item.available_quantity}):`, '0') || '0');
    if (qty > 0 && qty <= item.available_quantity) {
      try {
        await api.post('/resources/dispatch', {
          inventory_id: item.id,
          movement_type: 'dispatch',
          quantity: qty,
        });
        loadData();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to dispatch');
      }
    }
  };

  const handleReceive = async (item) => {
    const qty = parseInt(window.prompt('Receive quantity:', '0') || '0');
    if (qty > 0) {
      try {
        await api.post('/resources/receive', {
          inventory_id: item.id,
          movement_type: 'receive',
          quantity: qty,
        });
        loadData();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to receive');
      }
    }
  };

  if (loading) return <LoadingScreen />;

  const lowStockItems = inventory.filter(i => i.available_quantity <= i.minimum_threshold);

  return (
    <div>
      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-md)' }}>{error}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600', marginBottom: 'var(--spacing-xs)' }}>Resources & Inventory</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Manage resource depots, inventory levels, and track movements</p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          {activeTab === 'depots' && (
            <button className="btn btn-primary" onClick={() => { setEditingDepot(null); setDepotForm({ name: '', longitude: 0, latitude: 0, capacity: 0 }); setShowDepotModal(true); }}>
              <span>+</span> Add Depot
            </button>
          )}
          {activeTab === 'inventory' && (
            <button className="btn btn-primary" onClick={() => { setEditingInventory(null); setInventoryForm({ depot_id: '', resource_type: 'food_packets', quantity: 0 }); setShowInventoryModal(true); }}>
              <span>+</span> Add Inventory
            </button>
          )}
        </div>
      </div>

      {lowStockItems.length > 0 && (
        <div className="alert alert-warning" style={{ marginBottom: 'var(--spacing-md)' }}>
          <strong>⚠ Low Stock Alert:</strong> {lowStockItems.length} resource(s) below minimum threshold
          <button className="btn btn-sm btn-secondary" style={{ marginLeft: 'var(--spacing-md)' }} onClick={() => setActiveTab('inventory')}>View</button>
        </div>
      )}

      <div style={{ display: 'flex', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--spacing-sm)' }}>
        {(['depots', 'inventory', 'movements']).map(tab => (
          <button
            key={tab}
            className={`btn ${activeTab === tab ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab(tab)}
            style={{ textTransform: 'capitalize' }}
          >
            {tab === 'depots' ? '🏪 Depots' : tab === 'inventory' ? '📦 Inventory' : '📋 Movements'}
          </button>
        ))}
      </div>

      {activeTab === 'depots' && (
        <div className="card">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Location</th>
                  <th>Capacity</th>
                  <th>Status</th>
                  <th>Contact</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {depots.map(depot => (
                  <tr key={depot.id}>
                    <td><strong>{depot.name}</strong></td>
                    <td>{depot.longitude?.toFixed(4)}, {depot.latitude?.toFixed(4)}</td>
                    <td>{depot.capacity?.toLocaleString() ?? 0}</td>
                    <td><span className={`badge ${depot.is_active ? 'badge-low' : 'badge-cancelled'}`}>{depot.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>{depot.contact_person || '—'} {depot.contact_phone && `(${depot.contact_phone})`}</td>
                    <td>
                      <button className="btn btn-sm btn-secondary" onClick={() => { setEditingDepot(depot); setDepotForm(depot); setShowDepotModal(true); }}>Edit</button>
                    </td>
                  </tr>
                ))}
                {!depots.length && <tr><td colSpan={6} className="text-center text-muted">No depots configured</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'inventory' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-md)' }}>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
              <select className="form-select" style={{ width: 'auto' }} defaultValue="" onChange={(e) => e.target.value && window.location.reload()}>
                <option value="">All Types</option>
                {RESOURCE_TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
              </select>
              <select className="form-select" style={{ width: 'auto' }} defaultValue="" onChange={(e) => e.target.value && window.location.reload()}>
                <option value="">All Depots</option>
                {depots.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Depot</th>
                  <th>Resource Type</th>
                  <th>Total</th>
                  <th>Reserved</th>
                  <th>Available</th>
                  <th>Threshold</th>
                  <th>Unit</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map(item => (
                  <tr key={item.id} style={{ background: item.available_quantity <= item.minimum_threshold ? '#fff4e6' : 'transparent' }}>
                    <td>{depots.find(d => d.id === item.depot_id)?.name || 'Unknown'}</td>
                    <td>{item.resource_type.replace('_', ' ')}</td>
                    <td>{item.quantity.toLocaleString()}</td>
                    <td>{item.reserved_quantity.toLocaleString()}</td>
                    <td><strong>{item.available_quantity.toLocaleString()}</strong></td>
                    <td>{item.minimum_threshold}</td>
                    <td>{item.unit}</td>
                    <td>
                      <span className={`badge ${item.available_quantity <= item.minimum_threshold ? 'badge-medium' : item.available_quantity === 0 ? 'badge-critical' : 'badge-low'}`}>
                        {item.available_quantity === 0 ? 'Out of Stock' : item.available_quantity <= item.minimum_threshold ? 'Low Stock' : 'OK'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                        <button className="btn btn-sm btn-secondary" onClick={() => handleDispatch(item)} disabled={item.available_quantity === 0}>Dispatch</button>
                        <button className="btn btn-sm btn-secondary" onClick={() => handleReceive(item)}>Receive</button>
                        <button className="btn btn-sm btn-secondary" onClick={() => { setEditingInventory(item); setInventoryForm(item); setShowInventoryModal(true); }}>Edit</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!inventory.length && <tr><td colSpan={9} className="text-center text-muted">No inventory records</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'movements' && (
        <div className="card">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Resource</th>
                  <th>Quantity</th>
                  <th>From Depot</th>
                  <th>To Depot</th>
                  <th>Mission</th>
                  <th>Reference</th>
                </tr>
              </thead>
              <tbody>
                {movements.map(m => (
                  <tr key={m.id}>
                    <td>{new Date(m.created_at).toLocaleString()}</td>
                    <td><span className={`badge badge-${m.movement_type === 'dispatch' ? 'high' : 'low'}`}>{m.movement_type}</span></td>
                    <td>{m.inventory_id.slice(0, 8)}...</td>
                    <td>{m.quantity.toLocaleString()}</td>
                    <td>{m.from_depot_id?.slice(0, 8) || '—'}</td>
                    <td>{m.to_depot_id?.slice(0, 8) || '—'}</td>
                    <td>{m.mission_id?.slice(0, 8) || '—'}</td>
                    <td>{m.reference_number || '—'}</td>
                  </tr>
                ))}
                {!movements.length && <tr><td colSpan={8} className="text-center text-muted">No movements recorded</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showDepotModal && (
        <div className="modal-overlay" onClick={() => { setShowDepotModal(false); setEditingDepot(null); }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{editingDepot ? 'Edit Depot' : 'Add New Depot'}</h2>
              <button className="modal-close" onClick={() => { setShowDepotModal(false); setEditingDepot(null); }}>×</button>
            </div>
            <form onSubmit={handleDepotSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Depot Name *</label>
                  <input type="text" className="form-input" required value={depotForm.name} onChange={e => setDepotForm({ ...depotForm, name: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Longitude *</label>
                    <input type="number" step="any" className="form-input" required value={depotForm.longitude} onChange={e => setDepotForm({ ...depotForm, longitude: parseFloat(e.target.value) })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Latitude *</label>
                    <input type="number" step="any" className="form-input" required value={depotForm.latitude} onChange={e => setDepotForm({ ...depotForm, latitude: parseFloat(e.target.value) })} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Address</label>
                  <input type="text" className="form-input" value={depotForm.address || ''} onChange={e => setDepotForm({ ...depotForm, address: e.target.value })} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Contact Person</label>
                    <input type="text" className="form-input" value={depotForm.contact_person || ''} onChange={e => setDepotForm({ ...depotForm, contact_person: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Contact Phone</label>
                    <input type="text" className="form-input" value={depotForm.contact_phone || ''} onChange={e => setDepotForm({ ...depotForm, contact_phone: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Capacity</label>
                    <input type="number" className="form-input" value={depotForm.capacity || 0} onChange={e => setDepotForm({ ...depotForm, capacity: parseInt(e.target.value) || 0 })} />
                  </div>
                </div>
                <div className="form-group">
                  <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                    <input type="checkbox" checked={depotForm.is_active} onChange={e => setDepotForm({ ...depotForm, is_active: e.target.checked })} />
                    Active
                  </label>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => { setShowDepotModal(false); setEditingDepot(null); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>{creating ? 'Saving...' : (editingDepot ? 'Update' : 'Create')}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showInventoryModal && (
        <div className="modal-overlay" onClick={() => { setShowInventoryModal(false); setEditingInventory(null); }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">{editingInventory ? 'Edit Inventory' : 'Add Inventory Item'}</h2>
              <button className="modal-close" onClick={() => { setShowInventoryModal(false); setEditingInventory(null); }}>×</button>
            </div>
            <form onSubmit={handleInventorySubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Depot *</label>
                  <select className="form-select" required value={inventoryForm.depot_id} onChange={e => setInventoryForm({ ...inventoryForm, depot_id: e.target.value })}>
                    <option value="">Select Depot</option>
                    {depots.filter(d => d.is_active).map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Resource Type *</label>
                  <select className="form-select" value={inventoryForm.resource_type} onChange={e => setInventoryForm({ ...inventoryForm, resource_type: e.target.value })}>
                    {RESOURCE_TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
                  </select>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Quantity *</label>
                    <input type="number" className="form-input" required value={inventoryForm.quantity} onChange={e => setInventoryForm({ ...inventoryForm, quantity: parseInt(e.target.value) || 0 })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Reserved Quantity</label>
                    <input type="number" className="form-input" value={inventoryForm.reserved_quantity || 0} onChange={e => setInventoryForm({ ...inventoryForm, reserved_quantity: parseInt(e.target.value) || 0 })} />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                  <div className="form-group">
                    <label className="form-label">Minimum Threshold</label>
                    <input type="number" className="form-input" value={inventoryForm.minimum_threshold || 10} onChange={e => setInventoryForm({ ...inventoryForm, minimum_threshold: parseInt(e.target.value) || 0 })} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Cost per Unit</label>
                    <input type="number" step="0.01" className="form-input" value={inventoryForm.cost_per_unit || 0} onChange={e => setInventoryForm({ ...inventoryForm, cost_per_unit: parseFloat(e.target.value) || 0 })} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Unit</label>
                  <input type="text" className="form-input" value={inventoryForm.unit || 'units'} onChange={e => setInventoryForm({ ...inventoryForm, unit: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Expiry Date</label>
                  <input type="date" className="form-input" value={inventoryForm.expiry_date ? inventoryForm.expiry_date.split('T')[0] : ''} onChange={e => setInventoryForm({ ...inventoryForm, expiry_date: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Batch Number</label>
                  <input type="text" className="form-input" value={inventoryForm.batch_number || ''} onChange={e => setInventoryForm({ ...inventoryForm, batch_number: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Notes</label>
                  <textarea className="form-input" rows={2} value={inventoryForm.notes || ''} onChange={e => setInventoryForm({ ...inventoryForm, notes: e.target.value })} />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => { setShowInventoryModal(false); setEditingInventory(null); }}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>{creating ? 'Saving...' : (editingInventory ? 'Update' : 'Create')}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
