import logging
from datetime import datetime, timedelta
from app.database.models import (
    Incident, AffectedZone, ResourceDepot, ResourceInventory,
    Personnel, Mission, DemandPrediction, ResourceAllocation,
    DisasterTypeEnum, IncidentStatusEnum, SeverityEnum, ZoneSeverityEnum,
    ResourceTypeEnum, PersonnelRoleEnum, MissionStatusEnum
)

logger = logging.getLogger(__name__)


def seed_database_if_empty(db):
    try:
        incident_count = db.query(Incident).count()
        if incident_count > 0:
            logger.info("Database already contains data, skipping seed.")
            return

        logger.info("Database is empty. Seeding initial demo data...")

        # 1. Depots
        depot1 = ResourceDepot(
            name="Bhubaneswar Regional Emergency Depot",
            longitude=85.8245,
            latitude=20.2961,
            address="State Disaster Management Complex, Bhubaneswar, Odisha",
            contact_person="Rajesh Sharma",
            contact_phone="+91 98201 12345",
            capacity=100000,
            is_active=True
        )
        depot2 = ResourceDepot(
            name="Visakhapatnam Coastal Logistics Base",
            longitude=83.2185,
            latitude=17.6868,
            address="Port Trust Logistics Zone, Visakhapatnam, Andhra Pradesh",
            contact_person="Priya Deshmukh",
            contact_phone="+91 98220 54321",
            capacity=75000,
            is_active=True
        )
        depot3 = ResourceDepot(
            name="Nagpur Central Forward Base",
            longitude=79.0882,
            latitude=21.1458,
            address="Civil Lines, Nagpur",
            contact_person="Amitabh Roy",
            contact_phone="+91 97110 99887",
            capacity=50000,
            is_active=True
        )
        db.add_all([depot1, depot2, depot3])
        db.flush()

        # 2. Inventory
        inventory_items = [
            # Depot 1
            ResourceInventory(depot_id=depot1.id, resource_type=ResourceTypeEnum.food_packets, quantity=25000, reserved_quantity=5000, unit="packets", minimum_threshold=2000, cost_per_unit=50.0),
            ResourceInventory(depot_id=depot1.id, resource_type=ResourceTypeEnum.water, quantity=50000, reserved_quantity=10000, unit="liters", minimum_threshold=5000, cost_per_unit=15.0),
            ResourceInventory(depot_id=depot1.id, resource_type=ResourceTypeEnum.medical_kits, quantity=3000, reserved_quantity=400, unit="kits", minimum_threshold=300, cost_per_unit=500.0),
            ResourceInventory(depot_id=depot1.id, resource_type=ResourceTypeEnum.shelter, quantity=1200, reserved_quantity=200, unit="tents", minimum_threshold=100, cost_per_unit=1500.0),
            ResourceInventory(depot_id=depot1.id, resource_type=ResourceTypeEnum.rescue_vehicles, quantity=25, reserved_quantity=5, unit="vehicles", minimum_threshold=5, cost_per_unit=50000.0),
            ResourceInventory(depot_id=depot1.id, resource_type=ResourceTypeEnum.generators, quantity=80, reserved_quantity=10, unit="units", minimum_threshold=15, cost_per_unit=12000.0),
            # Depot 2
            ResourceInventory(depot_id=depot2.id, resource_type=ResourceTypeEnum.food_packets, quantity=15000, reserved_quantity=2000, unit="packets", minimum_threshold=1500, cost_per_unit=50.0),
            ResourceInventory(depot_id=depot2.id, resource_type=ResourceTypeEnum.water, quantity=35000, reserved_quantity=5000, unit="liters", minimum_threshold=4000, cost_per_unit=15.0),
            ResourceInventory(depot_id=depot2.id, resource_type=ResourceTypeEnum.medical_kits, quantity=1800, reserved_quantity=200, unit="kits", minimum_threshold=200, cost_per_unit=500.0),
            ResourceInventory(depot_id=depot2.id, resource_type=ResourceTypeEnum.fuel, quantity=20000, reserved_quantity=3000, unit="liters", minimum_threshold=2000, cost_per_unit=95.0),
            ResourceInventory(depot_id=depot2.id, resource_type=ResourceTypeEnum.communication, quantity=150, reserved_quantity=20, unit="radios", minimum_threshold=20, cost_per_unit=3000.0),
            # Depot 3
            ResourceInventory(depot_id=depot3.id, resource_type=ResourceTypeEnum.food_packets, quantity=12000, reserved_quantity=1000, unit="packets", minimum_threshold=1000, cost_per_unit=50.0),
            ResourceInventory(depot_id=depot3.id, resource_type=ResourceTypeEnum.water, quantity=25000, reserved_quantity=2000, unit="liters", minimum_threshold=3000, cost_per_unit=15.0),
            ResourceInventory(depot_id=depot3.id, resource_type=ResourceTypeEnum.rescue_vehicles, quantity=15, reserved_quantity=2, unit="vehicles", minimum_threshold=3, cost_per_unit=50000.0),
        ]
        db.add_all(inventory_items)

        # 3. Personnel
        personnel_members = [
            Personnel(name="Vikram Rathore", email="vikram.r@ndrf.gov.in", phone="+91 98111 22334", role=PersonnelRoleEnum.coordinator, skills="Incident Management, Crisis Coordination", availability=True, depot_id=depot1.id, deployment_status="available"),
            Personnel(name="Sunita Rao", email="sunita.rao@medical.org", phone="+91 98222 33445", role=PersonnelRoleEnum.medical, skills="Triage, Trauma Surgery, Emergency Medicine", availability=True, depot_id=depot1.id, deployment_status="available"),
            Personnel(name="Arjun Nair", email="arjun.nair@rescue.in", phone="+91 98333 44556", role=PersonnelRoleEnum.rescuer, skills="Water Rescue, Ropes, Urban Search", availability=True, depot_id=depot1.id, deployment_status="deployed"),
            Personnel(name="Deepak Verma", email="deepak.v@logistics.net", phone="+91 98444 55667", role=PersonnelRoleEnum.logistics, skills="Supply Chain, Warehouse Ops, Heavy Vehicles", availability=True, depot_id=depot2.id, deployment_status="available"),
            Personnel(name="Fatima Sheikh", email="fatima.s@comms.org", phone="+91 98555 66778", role=PersonnelRoleEnum.communications, skills="Satellite Comms, VHF Radio, Network Setup", availability=True, depot_id=depot2.id, deployment_status="available"),
            Personnel(name="Rohan Kulkarni", email="rohan.k@volunteer.org", phone="+91 98666 77889", role=PersonnelRoleEnum.volunteer, skills="First Aid, Food Distribution, Navigation", availability=True, depot_id=depot3.id, deployment_status="available"),
            Personnel(name="Manish Patel", email="manish.p@driver.org", phone="+91 98777 88990", role=PersonnelRoleEnum.driver, skills="All-Terrain Transport, Heavy Rig, Amphibious Vehicles", availability=True, depot_id=depot1.id, deployment_status="available"),
        ]
        db.add_all(personnel_members)
        db.flush()

        # 4. Incidents
        inc1 = Incident(
            name="Odisha & Andhra Pradesh Severe Cyclone & Flash Flooding",
            disaster_type=DisasterTypeEnum.cyclone,
            severity=SeverityEnum.critical,
            status=IncidentStatusEnum.active,
            description="Severe cyclonic storm making landfall across coastal Andhra Pradesh and South Odisha yesterday, causing widespread flash flooding, storm surges, and extensive infrastructural damage.",
            longitude=84.3500,
            latitude=18.6500,
            affected_population=185000,
            estimated_affected_population=250000,
            reported_by="IMD & Disaster Operations Command (Odisha-AP)",
            start_date=datetime.utcnow() - timedelta(days=1)
        )
        inc2 = Incident(
            name="Satara Western Ghats Landslide",
            disaster_type=DisasterTypeEnum.landslide,
            severity=SeverityEnum.high,
            status=IncidentStatusEnum.active,
            description="Massive slope failure cutting off multiple mountain hamlets; search and rescue teams actively deploying clearing machinery.",
            longitude=73.9903,
            latitude=17.6805,
            affected_population=4200,
            estimated_affected_population=6000,
            reported_by="State Disaster Management Authority",
            start_date=datetime.utcnow() - timedelta(days=1)
        )
        inc3 = Incident(
            name="Vidarbha Severe Heatwave & Water Shortage",
            disaster_type=DisasterTypeEnum.drought,
            severity=SeverityEnum.medium,
            status=IncidentStatusEnum.monitoring,
            description="Extreme temperatures leading to acute rural drinking water deficit; tanker relief operations mobilized.",
            longitude=79.2961,
            latitude=20.9320,
            affected_population=32000,
            estimated_affected_population=45000,
            reported_by="District Collectorate",
            start_date=datetime.utcnow() - timedelta(days=5)
        )
        db.add_all([inc1, inc2, inc3])
        db.flush()

        # 5. Affected Zones
        z1 = AffectedZone(
            incident_id=inc1.id,
            name="Zone A - Ganjam & South Odisha Coastal Basin",
            severity=ZoneSeverityEnum.critical,
            impact_score=9.4,
            affected_population=98000,
            vulnerable_children=14000,
            vulnerable_elderly=11000,
            vulnerable_medical=3500,
            buildings_damaged=4200,
            buildings_destroyed=850,
            infrastructure_damage=0.85,
            centroid_longitude=84.8500,
            centroid_latitude=19.3200,
            assessment_notes="Severe storm surge and flash flood inundation along Rushikulya river lowlands; ODRAF and NDRF power boat teams conducting mass evacuations."
        )
        z2 = AffectedZone(
            incident_id=inc1.id,
            name="Zone B - Srikakulam & North Coastal Andhra Sector",
            severity=ZoneSeverityEnum.high,
            impact_score=8.6,
            affected_population=87000,
            vulnerable_children=12000,
            vulnerable_elderly=9500,
            vulnerable_medical=2200,
            buildings_damaged=2800,
            buildings_destroyed=350,
            infrastructure_damage=0.70,
            centroid_longitude=83.8900,
            centroid_latitude=18.3000,
            assessment_notes="Severed coastal highway connectivity, uprooted power transmission lines, and waterlogged coastal villages; food drops underway."
        )
        z3 = AffectedZone(
            incident_id=inc2.id,
            name="Zone Alpha - Mahabaleshwar Valley Route",
            severity=ZoneSeverityEnum.high,
            impact_score=8.1,
            affected_population=4200,
            vulnerable_children=580,
            vulnerable_elderly=490,
            vulnerable_medical=110,
            buildings_damaged=95,
            buildings_destroyed=28,
            infrastructure_damage=0.60,
            centroid_longitude=73.6607,
            centroid_latitude=17.9237,
            assessment_notes="Single access road blocked by boulder slide; heavy earthmoving machinery deployed."
        )
        db.add_all([z1, z2, z3])
        db.flush()

        # 6. Demand Predictions
        preds = [
            DemandPrediction(zone_id=z1.id, resource_type=ResourceTypeEnum.food_packets, predicted_quantity=28500, lower_bound=22800, upper_bound=34200, confidence_level=0.88, method="baseline_regression_v1", vulnerability_adjustment=1.2),
            DemandPrediction(zone_id=z1.id, resource_type=ResourceTypeEnum.water, predicted_quantity=42750, lower_bound=34200, upper_bound=51300, confidence_level=0.92, method="baseline_regression_v1", vulnerability_adjustment=1.2),
            DemandPrediction(zone_id=z1.id, resource_type=ResourceTypeEnum.medical_kits, predicted_quantity=1425, lower_bound=1140, upper_bound=1710, confidence_level=0.85, method="baseline_regression_v1", vulnerability_adjustment=1.2),
            DemandPrediction(zone_id=z1.id, resource_type=ResourceTypeEnum.rescue_vehicles, predicted_quantity=14, lower_bound=10, upper_bound=18, confidence_level=0.80, method="baseline_regression_v1", vulnerability_adjustment=1.2),
            DemandPrediction(zone_id=z2.id, resource_type=ResourceTypeEnum.food_packets, predicted_quantity=21600, lower_bound=17280, upper_bound=25920, confidence_level=0.84, method="baseline_regression_v1", vulnerability_adjustment=1.1),
            DemandPrediction(zone_id=z2.id, resource_type=ResourceTypeEnum.water, predicted_quantity=32400, lower_bound=25920, upper_bound=38880, confidence_level=0.89, method="baseline_regression_v1", vulnerability_adjustment=1.1),
        ]
        db.add_all(preds)

        # 7. Resource Allocations
        allocs = [
            ResourceAllocation(zone_id=z1.id, resource_type=ResourceTypeEnum.food_packets, allocated_quantity=12000, fulfilled_quantity=6000, source_depot_id=depot1.id, priority=5, status="approved", approved=True, approved_at=datetime.utcnow() - timedelta(hours=12)),
            ResourceAllocation(zone_id=z1.id, resource_type=ResourceTypeEnum.water, allocated_quantity=20000, fulfilled_quantity=10000, source_depot_id=depot1.id, priority=5, status="approved", approved=True, approved_at=datetime.utcnow() - timedelta(hours=12)),
            ResourceAllocation(zone_id=z1.id, resource_type=ResourceTypeEnum.medical_kits, allocated_quantity=1000, fulfilled_quantity=500, source_depot_id=depot1.id, priority=4, status="approved", approved=True, approved_at=datetime.utcnow() - timedelta(hours=8)),
            ResourceAllocation(zone_id=z2.id, resource_type=ResourceTypeEnum.food_packets, allocated_quantity=8000, fulfilled_quantity=0, source_depot_id=depot2.id, priority=3, status="planned", approved=False),
        ]
        db.add_all(allocs)

        # 8. Missions
        m1 = Mission(
            incident_id=inc1.id,
            zone_id=z1.id,
            depot_id=depot1.id,
            name="Operation Sagar-Rakshak Alpha",
            description="Emergency amphibious rescue and medical supply airdrop for marooned coastal communities in Ganjam and South Odisha lowlands.",
            status=MissionStatusEnum.in_progress,
            priority=1,
            departure_time=datetime.utcnow() - timedelta(hours=4),
            estimated_arrival=datetime.utcnow() + timedelta(hours=2),
            route_distance_km=165.0,
            estimated_duration_hours=3.5
        )
        m2 = Mission(
            incident_id=inc1.id,
            zone_id=z2.id,
            depot_id=depot2.id,
            name="Andhra-Odisha Highway Relief Convoy Beta",
            description="Heavy transport convoy delivering drinking water purification units, emergency ration packets, and satellite communication equipment.",
            status=MissionStatusEnum.assigned,
            priority=2,
            departure_time=datetime.utcnow() + timedelta(hours=1),
            estimated_arrival=datetime.utcnow() + timedelta(hours=6),
            route_distance_km=110.0,
            estimated_duration_hours=2.5
        )
        db.add_all([m1, m2])

        db.commit()
        logger.info("Database seeding successfully completed!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()

