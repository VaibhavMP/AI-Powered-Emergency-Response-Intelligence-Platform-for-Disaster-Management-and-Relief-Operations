from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import enum


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


class Coordinates(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)


class IncidentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    disaster_type: DisasterTypeEnum
    severity: SeverityEnum
    description: Optional[str] = None
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    affected_population: int = Field(default=0, ge=0)
    estimated_affected_population: int = Field(default=0, ge=0)
    reported_by: Optional[str] = None
    source_id: Optional[str] = None
    external_id: Optional[str] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    disaster_type: Optional[DisasterTypeEnum] = None
    status: Optional[IncidentStatusEnum] = None
    severity: Optional[SeverityEnum] = None
    description: Optional[str] = None
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    affected_population: Optional[int] = Field(None, ge=0)
    estimated_affected_population: Optional[int] = Field(None, ge=0)
    end_date: Optional[datetime] = None


class IncidentResponse(IncidentBase):
    id: UUID
    status: IncidentStatusEnum
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    page_size: int


class AffectedZoneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    severity: ZoneSeverityEnum
    affected_population: int = Field(default=0, ge=0)
    vulnerable_children: int = Field(default=0, ge=0)
    vulnerable_elderly: int = Field(default=0, ge=0)
    vulnerable_medical: int = Field(default=0, ge=0)
    buildings_damaged: int = Field(default=0, ge=0)
    buildings_destroyed: int = Field(default=0, ge=0)
    infrastructure_damage: float = Field(default=0.0, ge=0.0, le=1.0)
    assessment_notes: Optional[str] = None


class AffectedZoneCreate(AffectedZoneBase):
    incident_id: Optional[UUID] = None
    boundary_coordinates: Optional[List[List[float]]] = None
    centroid_longitude: Optional[float] = Field(None, ge=-180, le=180)
    centroid_latitude: Optional[float] = Field(None, ge=-90, le=90)


class AffectedZoneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    severity: Optional[ZoneSeverityEnum] = None
    affected_population: Optional[int] = Field(None, ge=0)
    vulnerable_children: Optional[int] = Field(None, ge=0)
    vulnerable_elderly: Optional[int] = Field(None, ge=0)
    vulnerable_medical: Optional[int] = Field(None, ge=0)
    buildings_damaged: Optional[int] = Field(None, ge=0)
    buildings_destroyed: Optional[int] = Field(None, ge=0)
    infrastructure_damage: Optional[float] = Field(None, ge=0.0, le=1.0)
    assessment_notes: Optional[str] = None
    impact_score: Optional[float] = Field(None, ge=0.0)


class AffectedZoneResponse(AffectedZoneBase):
    id: UUID
    incident_id: UUID
    impact_score: float
    assessment_timestamp: datetime
    centroid: Optional[Coordinates] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceDepotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    capacity: int = Field(default=0, ge=0)
    is_active: bool = True


class ResourceDepotCreate(ResourceDepotBase):
    pass


class ResourceDepotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ResourceDepotResponse(ResourceDepotBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceInventoryBase(BaseModel):
    resource_type: ResourceTypeEnum
    quantity: int = Field(default=0, ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    unit: str = Field(default="units", max_length=50)
    minimum_threshold: int = Field(default=10, ge=0)
    cost_per_unit: float = Field(default=0.0, ge=0.0)
    expiry_date: Optional[datetime] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None


class ResourceInventoryCreate(ResourceInventoryBase):
    depot_id: UUID


class ResourceInventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    reserved_quantity: Optional[int] = Field(None, ge=0)
    minimum_threshold: Optional[int] = Field(None, ge=0)
    cost_per_unit: Optional[float] = Field(None, ge=0.0)
    expiry_date: Optional[datetime] = None
    batch_number: Optional[str] = None
    notes: Optional[str] = None


class ResourceInventoryResponse(ResourceInventoryBase):
    id: UUID
    depot_id: UUID
    created_at: datetime
    updated_at: datetime
    available_quantity: int = 0

    model_config = ConfigDict(from_attributes=True)


class ResourceMovementCreate(BaseModel):
    inventory_id: UUID
    movement_type: str = Field(..., pattern="^(dispatch|receive|transfer|adjustment|return)$")
    quantity: int = Field(..., gt=0)
    from_depot_id: Optional[UUID] = None
    to_depot_id: Optional[UUID] = None
    mission_id: Optional[UUID] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class ResourceMovementResponse(BaseModel):
    id: UUID
    inventory_id: UUID
    movement_type: str
    quantity: int
    from_depot_id: Optional[UUID]
    to_depot_id: Optional[UUID]
    mission_id: Optional[UUID]
    reference_number: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonnelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: PersonnelRoleEnum
    skills: Optional[str] = None
    availability: bool = True
    depot_id: Optional[UUID] = None
    current_assignment: Optional[str] = None
    deployment_status: str = Field(default="available", max_length=50)
    certifications: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class PersonnelCreate(PersonnelBase):
    pass


class PersonnelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[PersonnelRoleEnum] = None
    skills: Optional[str] = None
    availability: Optional[bool] = None
    depot_id: Optional[UUID] = None
    current_assignment: Optional[str] = None
    deployment_status: Optional[str] = Field(None, max_length=50)
    certifications: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class PersonnelResponse(PersonnelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DemandPredictionCreate(BaseModel):
    zone_id: UUID
    resource_type: ResourceTypeEnum
    predicted_quantity: int = Field(..., ge=0)
    lower_bound: Optional[int] = Field(None, ge=0)
    upper_bound: Optional[int] = Field(None, ge=0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    method: str = Field(..., min_length=1, max_length=100)
    model_version: Optional[str] = None
    input_factors: Optional[str] = None
    vulnerability_adjustment: float = Field(default=1.0, ge=0.0)


class DemandPredictionResponse(BaseModel):
    id: UUID
    zone_id: UUID
    resource_type: ResourceTypeEnum
    predicted_quantity: int
    lower_bound: Optional[int]
    upper_bound: Optional[int]
    confidence_level: Optional[float]
    method: str
    model_version: Optional[str]
    input_factors: Optional[str]
    vulnerability_adjustment: float
    prediction_timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceAllocationBase(BaseModel):
    zone_id: UUID
    resource_type: ResourceTypeEnum
    allocated_quantity: int = Field(default=0, ge=0)
    source_depot_id: Optional[UUID] = None
    priority: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class ResourceAllocationCreate(ResourceAllocationBase):
    pass


class ResourceAllocationUpdate(BaseModel):
    allocated_quantity: Optional[int] = Field(None, ge=0)
    fulfilled_quantity: Optional[int] = Field(None, ge=0)
    source_depot_id: Optional[UUID] = None
    priority: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    notes: Optional[str] = None
    approved: Optional[bool] = None
    approved_by: Optional[UUID] = None


class ResourceAllocationResponse(ResourceAllocationBase):
    id: UUID
    fulfilled_quantity: int
    status: str
    approved: bool
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MissionSupplyManifestCreate(BaseModel):
    resource_type: ResourceTypeEnum
    quantity: int = Field(..., gt=0)
    unit: str = Field(default="units", max_length=50)
    notes: Optional[str] = None


class MissionSupplyManifestResponse(MissionSupplyManifestCreate):
    id: UUID
    mission_id: UUID
    loaded: bool
    delivered: bool

    model_config = ConfigDict(from_attributes=True)


class MissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    incident_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    depot_id: Optional[UUID] = None
    destination_depot_id: Optional[UUID] = None
    priority: int = Field(default=0, ge=0)


class MissionCreate(MissionBase):
    supply_manifest: List[MissionSupplyManifestCreate] = []


class MissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    incident_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    depot_id: Optional[UUID] = None
    destination_depot_id: Optional[UUID] = None
    status: Optional[MissionStatusEnum] = None
    priority: Optional[int] = Field(None, ge=0)
    departure_time: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    route_distance_km: Optional[float] = Field(None, ge=0.0)
    estimated_duration_hours: Optional[float] = Field(None, ge=0.0)
    notes: Optional[str] = None


class MissionResponse(MissionBase):
    id: UUID
    status: MissionStatusEnum
    departure_time: Optional[datetime]
    estimated_arrival: Optional[datetime]
    actual_arrival: Optional[datetime]
    completion_time: Optional[datetime]
    route_distance_km: Optional[float]
    estimated_duration_hours: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    supply_manifest: List[MissionSupplyManifestResponse] = []

    model_config = ConfigDict(from_attributes=True)


class MissionPersonnelCreate(BaseModel):
    personnel_id: UUID
    role: Optional[str] = None


class MissionPersonnelResponse(BaseModel):
    id: UUID
    mission_id: UUID
    personnel_id: UUID
    role: Optional[str]
    assigned_at: datetime
    personnel: PersonnelResponse

    model_config = ConfigDict(from_attributes=True)


class FieldReportCreate(BaseModel):
    report_type: str = Field(default="status", max_length=50)
    content: str = Field(..., min_length=1)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    people_assisted: int = Field(default=0, ge=0)
    resources_delivered: Optional[str] = None
    issues: Optional[str] = None


class FieldReportResponse(BaseModel):
    id: UUID
    mission_id: UUID
    submitted_by: Optional[UUID]
    report_type: str
    content: str
    location: Optional[Coordinates]
    people_assisted: int
    resources_delivered: Optional[str]
    issues: Optional[str]
    created_at: datetime
    submitter: Optional[PersonnelResponse] = None

    model_config = ConfigDict(from_attributes=True)


class DataSourceRecordResponse(BaseModel):
    id: UUID
    source_name: str
    source_type: Optional[str]
    incident_id: Optional[UUID]
    external_id: Optional[str]
    processed: bool
    processing_status: str
    error_message: Optional[str]
    retrieved_at: datetime
    processed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class DataSourceItem(BaseModel):
    id: str
    name: str
    type: str
    url: str
    description: str
    enabled: bool
    last_sync: Optional[datetime] = None
    status: str


class DashboardSummary(BaseModel):
    total_active_incidents: int
    critical_incidents: int
    high_incidents: int
    resources_available: int
    resources_deployed: int
    active_personnel: int
    people_affected: int
    people_assisted: int


class DashboardActivity(BaseModel):
    recent_incidents: List[IncidentResponse]
    recent_missions: List[MissionResponse]
    high_priority_alerts: List[dict]


class AllocationOptimizeRequest(BaseModel):
    incident_id: UUID
    priority_overrides: Optional[dict] = None
    transport_capacity: Optional[dict] = None


class AllocationOptimizeResponse(BaseModel):
    allocation_plan_id: UUID
    recommendations: List[ResourceAllocationResponse]
    unmet_demand: List[dict]
    unallocated_inventory: List[dict]
    coverage_summary: dict
    optimization_status: str
    message: Optional[str] = None


class DemandPredictionRequest(BaseModel):
    incident_id: UUID
    zone_ids: Optional[List[UUID]] = None
    vulnerability_adjustment: float = Field(default=1.0, ge=0.0, le=2.0)


class AnalyticsSummary(BaseModel):
    total_incidents: int
    total_resources_allocated: int
    total_resources_delivered: int
    total_people_affected: int
    total_people_assisted: int
    average_response_time_hours: Optional[float]
    mission_completion_rate: float
    unmet_demand_by_type: dict


class SituationReport(BaseModel):
    report_id: UUID
    incident_id: UUID
    incident_name: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    summary: str
    resources_allocated: dict
    resources_delivered: dict
    demand_vs_supply: dict
    zone_coverage: dict
    mission_stats: dict
    unmet_demand: dict
    recommendations: List[str]