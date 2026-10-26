from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean, CheckConstraint, Index, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.database.connection import Base


class DisasterTypeEnum(str, enum.Enum):
    flood = "flood"
    earthquake = "earthquake"
    cyclone = "cyclone"
    wildfire = "wildfire"
    drought = "drought"
    landslide = "landslide"
    tsunami = "tsunami"
    volcano = "volcano"
    other = "other"


class IncidentStatusEnum(str, enum.Enum):
    active = "active"
    monitoring = "monitoring"
    contained = "contained"
    recovered = "recovered"
    closed = "closed"


class SeverityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    recovery = "recovery"


class ResourceTypeEnum(str, enum.Enum):
    food_packets = "food_packets"
    water = "water"
    medical_kits = "medical_kits"
    shelter = "shelter"
    rescue_vehicles = "rescue_vehicles"
    personnel = "personnel"
    fuel = "fuel"
    generators = "generators"
    communication = "communication"
    other = "other"


class PersonnelRoleEnum(str, enum.Enum):
    coordinator = "coordinator"
    rescuer = "rescuer"
    medical = "medical"
    logistics = "logistics"
    driver = "driver"
    communications = "communications"
    volunteer = "volunteer"
    other = "other"


class MissionStatusEnum(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class ZoneSeverityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    disaster_type = Column(Enum(DisasterTypeEnum), nullable=False)
    status = Column(Enum(IncidentStatusEnum), default=IncidentStatusEnum.active, nullable=False)
    severity = Column(Enum(SeverityEnum), nullable=False)
    description = Column(Text, nullable=True)
    longitude = Column(Float, nullable=False, default=0.0)
    latitude = Column(Float, nullable=False, default=0.0)
    affected_population = Column(Integer, default=0)
    estimated_affected_population = Column(Integer, default=0)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    reported_by = Column(String(255), nullable=True)
    source_id = Column(String(255), nullable=True)
    external_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    zones = relationship("AffectedZone", back_populates="incident", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="incident")
    data_source_records = relationship("DataSourceRecord", back_populates="incident")

    @property
    def location(self):
        return {"longitude": self.longitude, "latitude": self.latitude}

    __table_args__ = (
        Index('ix_incidents_status', 'status'),
        Index('ix_incidents_disaster_type', 'disaster_type'),
        Index('ix_incidents_severity', 'severity'),
    )


class AffectedZone(Base):
    __tablename__ = "affected_zones"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id = Column(Uuid, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    boundary_coordinates = Column(Text, nullable=True)
    centroid_longitude = Column(Float, nullable=True)
    centroid_latitude = Column(Float, nullable=True)
    severity = Column(Enum(ZoneSeverityEnum), nullable=False)
    impact_score = Column(Float, default=0.0)
    affected_population = Column(Integer, default=0)
    vulnerable_children = Column(Integer, default=0)
    vulnerable_elderly = Column(Integer, default=0)
    vulnerable_medical = Column(Integer, default=0)
    buildings_damaged = Column(Integer, default=0)
    buildings_destroyed = Column(Integer, default=0)
    infrastructure_damage = Column(Float, default=0.0)
    assessment_notes = Column(Text, nullable=True)
    assessment_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    incident = relationship("Incident", back_populates="zones")
    demand_predictions = relationship("DemandPrediction", back_populates="zone", cascade="all, delete-orphan")
    allocations = relationship("ResourceAllocation", back_populates="zone", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="zone")

    @property
    def centroid(self):
        if self.centroid_longitude is not None and self.centroid_latitude is not None:
            return {"longitude": self.centroid_longitude, "latitude": self.centroid_latitude}
        return None

    __table_args__ = (
        Index('ix_affected_zones_incident_id', 'incident_id'),
        Index('ix_affected_zones_severity', 'severity'),
    )


class ResourceDepot(Base):
    __tablename__ = "resource_depots"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    longitude = Column(Float, nullable=False, default=0.0)
    latitude = Column(Float, nullable=False, default=0.0)
    address = Column(String(500), nullable=True)
    contact_person = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    capacity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    inventory = relationship("ResourceInventory", back_populates="depot", cascade="all, delete-orphan")
    missions_from = relationship("Mission", back_populates="depot", foreign_keys="Mission.depot_id")
    missions_to = relationship("Mission", back_populates="destination_depot", foreign_keys="Mission.destination_depot_id")

    @property
    def location(self):
        return {"longitude": self.longitude, "latitude": self.latitude}


class ResourceInventory(Base):
    __tablename__ = "resource_inventory"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    depot_id = Column(Uuid, ForeignKey("resource_depots.id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(Enum(ResourceTypeEnum), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0)
    unit = Column(String(50), default="units")
    minimum_threshold = Column(Integer, default=10)
    cost_per_unit = Column(Float, default=0.0)
    expiry_date = Column(DateTime, nullable=True)
    batch_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    depot = relationship("ResourceDepot", back_populates="inventory")
    movements = relationship("ResourceMovement", back_populates="inventory_item")

    __table_args__ = (
        UniqueConstraint('depot_id', 'resource_type', name='uq_depot_resource_type'),
        CheckConstraint('quantity >= 0', name='ck_inventory_quantity_nonnegative'),
        CheckConstraint('reserved_quantity >= 0', name='ck_inventory_reserved_nonnegative'),
        CheckConstraint('reserved_quantity <= quantity', name='ck_inventory_reserved_not_exceed'),
    )


class ResourceMovement(Base):
    __tablename__ = "resource_movements"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    inventory_id = Column(Uuid, ForeignKey("resource_inventory.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    from_depot_id = Column(Uuid, ForeignKey("resource_depots.id"), nullable=True)
    to_depot_id = Column(Uuid, ForeignKey("resource_depots.id"), nullable=True)
    mission_id = Column(Uuid, ForeignKey("missions.id"), nullable=True)
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    inventory_item = relationship("ResourceInventory", back_populates="movements")
    from_depot = relationship("ResourceDepot", foreign_keys=[from_depot_id])
    to_depot = relationship("ResourceDepot", foreign_keys=[to_depot_id])

    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_movement_quantity_positive'),
    )


class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    role = Column(Enum(PersonnelRoleEnum), nullable=False)
    skills = Column(Text, nullable=True)
    availability = Column(Boolean, default=True)
    depot_id = Column(Uuid, ForeignKey("resource_depots.id"), nullable=True)
    current_assignment = Column(String(255), nullable=True)
    deployment_status = Column(String(50), default="available")
    certifications = Column(Text, nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    emergency_phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    depot = relationship("ResourceDepot")
    mission_assignments = relationship("MissionPersonnel", back_populates="personnel")


class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    zone_id = Column(Uuid, ForeignKey("affected_zones.id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(Enum(ResourceTypeEnum), nullable=False)
    predicted_quantity = Column(Integer, nullable=False)
    lower_bound = Column(Integer, nullable=True)
    upper_bound = Column(Integer, nullable=True)
    confidence_level = Column(Float, nullable=True)
    method = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    input_factors = Column(Text, nullable=True)
    vulnerability_adjustment = Column(Float, default=1.0)
    prediction_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    zone = relationship("AffectedZone", back_populates="demand_predictions")

    __table_args__ = (
        Index('ix_demand_predictions_zone_id', 'zone_id'),
        Index('ix_demand_predictions_resource_type', 'resource_type'),
    )


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    zone_id = Column(Uuid, ForeignKey("affected_zones.id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(Enum(ResourceTypeEnum), nullable=False)
    allocated_quantity = Column(Integer, default=0)
    fulfilled_quantity = Column(Integer, default=0)
    source_depot_id = Column(Uuid, ForeignKey("resource_depots.id"), nullable=True)
    priority = Column(Integer, default=0)
    status = Column(String(50), default="planned")
    notes = Column(Text, nullable=True)
    approved = Column(Boolean, default=False)
    approved_by = Column(Uuid, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    zone = relationship("AffectedZone", back_populates="allocations")
    source_depot = relationship("ResourceDepot")

    __table_args__ = (
        Index('ix_resource_allocations_zone_id', 'zone_id'),
        Index('ix_resource_allocations_resource_type', 'resource_type'),
        CheckConstraint('allocated_quantity >= 0', name='ck_allocation_quantity_nonnegative'),
        CheckConstraint('fulfilled_quantity >= 0', name='ck_allocation_fulfilled_nonnegative'),
    )


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    incident_id = Column(Uuid, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    zone_id = Column(Uuid, ForeignKey("affected_zones.id", ondelete="SET NULL"), nullable=True)
    depot_id = Column(Uuid, ForeignKey("resource_depots.id"), nullable=True)
    destination_depot_id = Column(Uuid, ForeignKey("resource_depots.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MissionStatusEnum), default=MissionStatusEnum.pending, nullable=False)
    priority = Column(Integer, default=0)
    departure_time = Column(DateTime, nullable=True)
    estimated_arrival = Column(DateTime, nullable=True)
    actual_arrival = Column(DateTime, nullable=True)
    completion_time = Column(DateTime, nullable=True)
    route_geometry = Column(Text, nullable=True)
    route_distance_km = Column(Float, nullable=True)
    estimated_duration_hours = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    incident = relationship("Incident", back_populates="missions")
    zone = relationship("AffectedZone", back_populates="missions")
    depot = relationship("ResourceDepot", back_populates="missions_from", foreign_keys=[depot_id])
    destination_depot = relationship("ResourceDepot", back_populates="missions_to", foreign_keys=[destination_depot_id])
    personnel = relationship("MissionPersonnel", back_populates="mission", cascade="all, delete-orphan")
    supply_manifest = relationship("MissionSupplyManifest", back_populates="mission", cascade="all, delete-orphan")
    field_reports = relationship("FieldReport", back_populates="mission", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_missions_status', 'status'),
        Index('ix_missions_incident_id', 'incident_id'),
    )


class MissionPersonnel(Base):
    __tablename__ = "mission_personnel"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    mission_id = Column(Uuid, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    personnel_id = Column(Uuid, ForeignKey("personnel.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mission = relationship("Mission", back_populates="personnel")
    personnel = relationship("Personnel", back_populates="mission_assignments")

    __table_args__ = (
        UniqueConstraint('mission_id', 'personnel_id', name='uq_mission_personnel'),
    )


class MissionSupplyManifest(Base):
    __tablename__ = "mission_supply_manifest"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    mission_id = Column(Uuid, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(Enum(ResourceTypeEnum), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(50), default="units")
    loaded = Column(Boolean, default=False)
    delivered = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    mission = relationship("Mission", back_populates="supply_manifest")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_manifest_quantity_positive'),
    )


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    mission_id = Column(Uuid, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    submitted_by = Column(Uuid, ForeignKey("personnel.id"), nullable=True)
    report_type = Column(String(50), default="status")
    content = Column(Text, nullable=False)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    people_assisted = Column(Integer, default=0)
    resources_delivered = Column(Text, nullable=True)
    issues = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mission = relationship("Mission", back_populates="field_reports")
    submitter = relationship("Personnel")

    @property
    def location(self):
        if self.longitude is not None and self.latitude is not None:
            return {"longitude": self.longitude, "latitude": self.latitude}
        return None


class DataSourceRecord(Base):
    __tablename__ = "data_source_records"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    source_name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=True)
    incident_id = Column(Uuid, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    external_id = Column(String(255), nullable=True)
    raw_data = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="data_source_records")

    __table_args__ = (
        Index('ix_data_source_records_source_name', 'source_name'),
        Index('ix_data_source_records_processed', 'processed'),
    )
