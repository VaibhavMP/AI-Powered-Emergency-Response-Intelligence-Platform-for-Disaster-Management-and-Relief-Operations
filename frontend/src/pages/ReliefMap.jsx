import { useState, useEffect, useRef } from 'react';
import { LoadingScreen } from '../components/LoadingScreen';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from 'react-leaflet';
import { Link } from 'react-router-dom';
import L from 'leaflet';
import { api } from '../api/client';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const severityColors = {
  critical: '#8b0000',
  high: '#dc3545',
  medium: '#fd7e14',
  low: '#28a745',
  recovery: '#17a2b8',
};

export function ReliefMap() {
  const [incidents, setIncidents] = useState([]);
  const [zones, setZones] = useState([]);
  const [depots, setDepots] = useState([]);
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showLayers, setShowLayers] = useState({
    incidents: true,
    zones: true,
    depots: true,
    missions: true,
  });
  const [selectedFeature, setSelectedFeature] = useState(null);

  useEffect(() => {
    loadMapData();
  }, []);

  const loadMapData = async () => {
    try {
      setLoading(true);
      const [incidentsData, depotsData, missionsData] = await Promise.all([
        api.get('/incidents?page_size=100'),
        api.get('/depots'),
        api.get('/missions?page_size=100'),
      ]);
      setIncidents(incidentsData.items || incidentsData);
      setDepots(depotsData);
      setMissions(missionsData);

      const allZones = [];
      for (const inc of incidentsData.items || incidentsData) {
        try {
          const zonesData = await api.get(`/incidents/${inc.id}/zones`);
          allZones.push(...zonesData);
        } catch {}
      }
      setZones(allZones);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load map data');
    } finally {
      setLoading(false);
    }
  };

  const getLatLng = (item) => [item.latitude, item.longitude];
  const getZoneLatLng = (zone) => zone.centroid ? [zone.centroid.latitude, zone.centroid.longitude] : [0, 0];

  const allFeatures = [
    ...incidents.map(i => ({ ...i, type: 'incident', latlng: getLatLng(i) })),
    ...depots.map(d => ({ ...d, type: 'depot', latlng: getLatLng(d) })),
    ...zones.map(z => ({ ...z, type: 'zone', latlng: getZoneLatLng(z) })),
  ];

  const validFeatures = allFeatures.filter(f => f.latlng[0] !== 0 || f.latlng[1] !== 0);
  const center = validFeatures.length > 0
    ? [validFeatures.reduce((sum, f) => sum + f.latlng[0], 0) / validFeatures.length, validFeatures.reduce((sum, f) => sum + f.latlng[1], 0) / validFeatures.length]
    : [20.5937, 78.9629];

  if (loading) return <LoadingScreen />;

  return (
    <div style={{ height: 'calc(100vh - 140px)', minHeight: '600px' }}>
      {error && <div className="alert alert-error" style={{ position: 'absolute', top: 'var(--spacing-md)', left: 'var(--spacing-md)', right: 'var(--spacing-md)', zIndex: 1000 }}>{error}</div>}

      <div style={{ position: 'absolute', top: 'var(--spacing-md)', right: 'var(--spacing-md)', zIndex: 1000, background: 'var(--color-surface)', padding: 'var(--spacing-sm)', borderRadius: 'var(--radius-md)', boxShadow: 'var(--color-shadow)', border: '1px solid var(--color-border)' }}>
        <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: 'var(--spacing-xs)', color: 'var(--color-text)' }}>Map Layers</div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-xs)', cursor: 'pointer' }}>
          <input type="checkbox" checked={showLayers.incidents} onChange={(e) => setShowLayers({ ...showLayers, incidents: e.target.checked })} />
          <span style={{ fontSize: '13px' }}>Incidents ({incidents.length})</span>
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-xs)', cursor: 'pointer' }}>
          <input type="checkbox" checked={showLayers.zones} onChange={(e) => setShowLayers({ ...showLayers, zones: e.target.checked })} />
          <span style={{ fontSize: '13px' }}>Affected Zones ({zones.length})</span>
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-xs)', cursor: 'pointer' }}>
          <input type="checkbox" checked={showLayers.depots} onChange={(e) => setShowLayers({ ...showLayers, depots: e.target.checked })} />
          <span style={{ fontSize: '13px' }}>Depots ({depots.length})</span>
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', cursor: 'pointer' }}>
          <input type="checkbox" checked={showLayers.missions} onChange={(e) => setShowLayers({ ...showLayers, missions: e.target.checked })} />
          <span style={{ fontSize: '13px' }}>Missions ({missions.length})</span>
        </label>
      </div>

      <MapContainer center={center} zoom={5} style={{ width: '100%', height: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {showLayers.incidents && incidents.map((inc) => (
          <Marker key={inc.id} position={getLatLng(inc)}>
            <Popup>
              <div style={{ minWidth: 200 }}>
                <h4 style={{ margin: '0 0 var(--spacing-xs)', color: 'var(--color-primary)' }}>{inc.name}</h4>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Type:</strong> {inc.disaster_type}</p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Severity:</strong> <span className={`badge badge-${inc.severity}`}>{inc.severity}</span></p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Status:</strong> <span className={`badge badge-${inc.status}`}>{inc.status}</span></p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Population:</strong> {inc.affected_population?.toLocaleString() ?? 0}</p>
                <Link to={`/incidents/${inc.id}`} style={{ display: 'inline-block', marginTop: 'var(--spacing-xs)', fontSize: '13px' }}>View Details →</Link>
              </div>
            </Popup>
          </Marker>
        ))}

        {showLayers.zones && zones.map((zone) => (
          <Circle
            key={zone.id}
            center={getZoneLatLng(zone)}
            radius={Math.max(1000, Math.sqrt(zone.affected_population || 1) * 100)}
            color={severityColors[zone.severity] || '#8b0000'}
            fillColor={severityColors[zone.severity] || '#8b0000'}
            fillOpacity={0.2}
            weight={2}
          >
            <Popup>
              <div style={{ minWidth: 200 }}>
                <h4 style={{ margin: '0 0 var(--spacing-xs)', color: 'var(--color-primary)' }}>{zone.name}</h4>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Severity:</strong> <span className={`badge badge-${zone.severity}`}>{zone.severity}</span></p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Population:</strong> {zone.affected_population?.toLocaleString() ?? 0}</p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Impact Score:</strong> {zone.impact_score?.toFixed(2) ?? 0}</p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Vulnerable:</strong> {zone.vulnerable_children}C/{zone.vulnerable_elderly}E/{zone.vulnerable_medical}M</p>
              </div>
            </Popup>
          </Circle>
        ))}

        {showLayers.depots && depots.map((depot) => (
          <Marker key={depot.id} position={getLatLng(depot)}>
            <Popup>
              <div style={{ minWidth: 200 }}>
                <h4 style={{ margin: '0 0 var(--spacing-xs)', color: 'var(--color-low)' }}>{depot.name}</h4>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Capacity:</strong> {depot.capacity}</p>
                <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Status:</strong> {depot.is_active ? 'Active' : 'Inactive'}</p>
                {depot.address && <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Address:</strong> {depot.address}</p>}
              </div>
            </Popup>
          </Marker>
        ))}

        {showLayers.missions && missions.map((mission) => {
          if (mission.depot_id && mission.destination_depot_id) {
            const depot = depots.find(d => d.id === mission.depot_id);
            const destDepot = depots.find(d => d.id === mission.destination_depot_id);
            if (depot && destDepot) {
              return (
                <Polyline
                  key={mission.id}
                  positions={[[depot.latitude, depot.longitude], [destDepot.latitude, destDepot.longitude]]}
                  color="#007bff"
                  weight={2}
                  dashArray="5, 10"
                >
                  <Popup>
                    <div style={{ minWidth: 200 }}>
                      <h4 style={{ margin: '0 0 var(--spacing-xs)' }}>{mission.name}</h4>
                      <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>Status:</strong> <span className={`badge badge-${mission.status}`}>{mission.status}</span></p>
                      <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>From:</strong> {depot.name}</p>
                      <p style={{ margin: 'var(--spacing-xs) 0', fontSize: '13px' }}><strong>To:</strong> {destDepot.name}</p>
                    </div>
                  </Popup>
                </Polyline>
              );
            }
          }
          return null;
        })}

        <div className="leaflet-control leaflet-control-custom" style={{
          position: 'absolute',
          bottom: 'var(--spacing-md)',
          left: 'var(--spacing-md)',
          background: 'var(--color-surface)',
          padding: 'var(--spacing-sm)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--color-shadow)',
          border: '1px solid var(--color-border)',
          zIndex: 1000,
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)', fontSize: '11px' }}>
            <div><span style={{ display: 'inline-block', width: 12, height: 12, background: '#8b0000', borderRadius: '50%', marginRight: 'var(--spacing-xs)' }}></span>Critical</div>
            <div><span style={{ display: 'inline-block', width: 12, height: 12, background: '#dc3545', borderRadius: '50%', marginRight: 'var(--spacing-xs)' }}></span>High</div>
            <div><span style={{ display: 'inline-block', width: 12, height: 12, background: '#fd7e14', borderRadius: '50%', marginRight: 'var(--spacing-xs)' }}></span>Medium</div>
            <div><span style={{ display: 'inline-block', width: 12, height: 12, background: '#28a745', borderRadius: '50%', marginRight: 'var(--spacing-xs)' }}></span>Low</div>
            <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--spacing-xs)', marginTop: 'var(--spacing-xs)' }}>
              <div><span style={{ display: 'inline-block', width: 12, height: 12, border: '2px solid #8b0000', borderRadius: '50%', marginRight: 'var(--spacing-xs)', background: 'transparent' }}></span>Incidents</div>
              <div><span style={{ display: 'inline-block', width: 12, height: 12, border: '2px solid #28a745', borderRadius: '50%', marginRight: 'var(--spacing-xs)', background: 'transparent' }}></span>Depots</div>
            </div>
          </div>
        </div>
      </MapContainer>
    </div>
  );
}
