import sys
sys.path.insert(0, r'.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test health
print('=== /health ===')
resp = client.get('/health')
print(f'Status: {resp.status_code}, Body: {resp.json()}')

# Test root
print()
print('=== / ===')
resp = client.get('/')
print(f'Status: {resp.status_code}, Body: {resp.json()}')

# Test dashboard summary
print()
print('=== /api/dashboard/summary ===')
resp = client.get('/api/dashboard/summary')
print(f'Status: {resp.status_code}, Body: {resp.json()}')

# Test dashboard activity
print()
print('=== /api/dashboard/activity?limit=5 ===')
resp = client.get('/api/dashboard/activity?limit=5')
print(f'Status: {resp.status_code}, Body: {resp.json()}')

# Test incidents list
print()
print('=== /api/incidents?page_size=5 ===')
resp = client.get('/api/incidents?page_size=5')
print(f'Status: {resp.status_code}, Items: {len(resp.json().get("items", []))}, Total: {resp.json().get("total", 0)}')

# Test creating an incident
print()
print('=== POST /api/incidents ===')
new_incident = {
    'name': 'Test Flood Incident',
    'disaster_type': 'flood',
    'severity': 'medium',
    'description': 'Test incident for verification',
    'longitude': -95.0,
    'latitude': 29.0,
    'affected_population': 1000,
    'estimated_affected_population': 1500,
}
resp = client.post('/api/incidents', json=new_incident)
print(f'Status: {resp.status_code}')
if resp.status_code == 201:
    created = resp.json()
    print(f'Created incident ID: {created["id"]}')
    incident_id = created['id']
    
    # Test getting the incident
    print(f'=== GET /api/incidents/{incident_id} ===')
    resp = client.get(f'/api/incidents/{incident_id}')
    print(f'Status: {resp.status_code}, Name: {resp.json()["name"]}')
    
    # Test updating the incident
    print(f'=== PATCH /api/incidents/{incident_id} ===')
    resp = client.patch(f'/api/incidents/{incident_id}', json={'status': 'contained'})
    print(f'Status: {resp.status_code}, Status: {resp.json()["status"]}')
    
    # Test creating a zone
    print(f'=== POST /api/incidents/{incident_id}/zones ===')
    new_zone = {
        'name': 'Test Zone',
        'severity': 'medium',
        'affected_population': 500,
        'vulnerable_children': 50,
        'vulnerable_elderly': 25,
        'vulnerable_medical': 10,
        'buildings_damaged': 5,
        'buildings_destroyed': 2,
        'infrastructure_damage': 0.1,
    }
    resp = client.post(f'/api/incidents/{incident_id}/zones', json=new_zone)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 201:
        created_zone = resp.json()
        zone_id = created_zone['id']
        print(f'Created zone ID: {zone_id}')
        
        # Test getting the zone
        print(f'=== GET /api/zones/{zone_id} ===')
        resp = client.get(f'/api/zones/{zone_id}')
        print(f'Status: {resp.status_code}, Name: {resp.json()["name"]}')
        
        # Test listing resources
        print(f'=== /api/resources ===')
        resp = client.get('/api/resources')
        print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
        
        # Test listing personnel
        print(f'=== /api/personnel ===')
        resp = client.get('/api/personnel')
        print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
        
        # Test creating personnel
        print(f'=== POST /api/personnel ===')
        new_personnel = {
            'name': 'John Rescuer',
            'role': 'rescuer',
            'skills': 'First Aid, Navigation',
        }
        resp = client.post('/api/personnel', json=new_personnel)
        print(f'Status: {resp.status_code}')
        if resp.status_code == 201:
            created_personnel = resp.json()
            personnel_id = created_personnel['id']
            print(f'Created personnel ID: {personnel_id}')
            
            # Test listing missions
            print(f'=== /api/missions?page_size=5 ===')
            resp = client.get('/api/missions?page_size=5')
            print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
            
            # Test creating a mission
            print(f'=== POST /api/missions ===')
            new_mission = {
                'name': 'Test Search Mission',
                'description': 'Search and rescue operation',
                'priority': 1,
            }
            resp = client.post('/api/missions', json=new_mission)
            print(f'Status: {resp.status_code}')
            if resp.status_code == 201:
                created_mission = resp.json()
                mission_id = created_mission['id']
                print(f'Created mission ID: {mission_id}')
                
                # Test assigning personnel
                print(f'=== POST /api/missions/{mission_id}/personnel ===')
                resp = client.post(f'/api/missions/{mission_id}/personnel', json={'personnel_id': personnel_id, 'role': 'rescuer'})
                print(f'Status: {resp.status_code}')
                
                # Test predictions
                print(f'=== /api/predictions?page_size=5 ===')
                resp = client.get('/api/predictions?page_size=5')
                print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
                
                # Test running prediction
                print(f'=== POST /api/predictions/predict ===')
                resp = client.post('/api/predictions/predict', json={'incident_id': incident_id, 'vulnerability_adjustment': 1.0})
                print(f'Status: {resp.status_code}')
                if resp.status_code == 200:
                    predictions = resp.json()
                    print(f'Generated {len(predictions)} predictions')
                
                # Test allocations
                print(f'=== /api/allocations?page_size=5 ===')
                resp = client.get('/api/allocations?page_size=5')
                print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
                
                # Test approval
                print(f'=== POST /api/allocations/approve ===')
                alloc_resp = client.get('/api/allocations?page_size=1')
                if alloc_resp.json():
                    first_alloc = alloc_resp.json()[0]
                    print(f'Approving allocation {first_alloc["id"]}')
                    resp = client.post(f'/api/allocations/{first_alloc["id"]}/approve')
                    print(f'Status: {resp.status_code}')
                
                # Test reports
                print(f'=== /api/reports ===')
                resp = client.get('/api/reports')
                print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
                
                # Test data sources
                print(f'=== /api/data-sources ===')
                resp = client.get('/api/data-sources')
                print(f'Status: {resp.status_code}, Items: {len(resp.json())}')
                
                # Test analytics
                print(f'=== /api/analytics/summary ===')
                resp = client.get('/api/analytics/summary')
                print(f'Status: {resp.status_code}')
                if resp.status_code == 200:
                    print(f'Body: {resp.json()}')
        
print()
print('=== All endpoint tests completed ===')