export interface Coordinates {
  longitude: number;
  latitude: number;
}

export interface Incident {
  id: string;
  name: string;
  disaster_type: string;
  status: string;
  severity: string;
  description: string | null;
  longitude: number;
  latitude: number;
  affected_population: number;
  estimated_affected_population: number;
  start_date: string;
  end_date: string | null;
  reported_by: string | null;
  source_id: string | null;
  external_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface IncidentListResponse {
  items: Incident[];
  total: number;
  page: number;
  page_size: number;
}

export interface IncidentCreate {
  name: string;
  disaster_type: string;
  severity: string;
  description?: string;
  longitude: number;
  latitude: number;
  affected_population?: number;
  estimated_affected_population?: number;
  reported_by?: string;
  source_id?: string;
  external_id?: string;
}

export interface IncidentUpdate {
  name?: string;
  disaster_type?: string;
  status?: string;
  severity?: string;
  description?: string;
  longitude?: number;
  latitude?: number;
  affected_population?: number;
  estimated_affected_population?: number;
  end_date?: string;
}

export interface AffectedZone {
  id: string;
  incident_id: string;
  name: string;
  severity: string;
  impact_score: number;
  affected_population: number;
  vulnerable_children: number;
  vulnerable_elderly: number;
  vulnerable_medical: number;
  buildings_damaged: number;
  buildings_destroyed: number;
  infrastructure_damage: number;
  assessment_notes: string | null;
  assessment_timestamp: string;
  centroid: Coordinates | null;
  created_at: string;
  updated_at: string;
}

export interface AffectedZoneCreate {
  incident_id: string;
  name: string;
  severity: string;
  affected_population?: number;
  vulnerable_children?: number;
  vulnerable_elderly?: number;
  vulnerable_medical?: number;
  buildings_damaged?: number;
  buildings_destroyed?: number;
  infrastructure_damage?: number;
  assessment_notes?: string;
  boundary_coordinates?: number[][][];
  centroid_longitude?: number;
  centroid_latitude?: number;
}

export interface AffectedZoneUpdate {
  name?: string;
  severity?: string;
  affected_population?: number;
  vulnerable_children?: number;
  vulnerable_elderly?: number;
  vulnerable_medical?: number;
  buildings_damaged?: number;
  buildings_destroyed?: number;
  infrastructure_damage?: number;
  assessment_notes?: string;
  impact_score?: number;
}

export interface ResourceDepot {
  id: string;
  name: string;
  longitude: number;
  latitude: number;
  address: string | null;
  contact_person: string | null;
  contact_phone: string | null;
  capacity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResourceDepotCreate {
  name: string;
  longitude: number;
  latitude: number;
  address?: string;
  contact_person?: string;
  contact_phone?: string;
  capacity?: number;
  is_active?: boolean;
}

export interface ResourceDepotUpdate {
  name?: string;
  longitude?: number;
  latitude?: number;
  address?: string;
  contact_person?: string;
  contact_phone?: string;
  capacity?: number;
  is_active?: boolean;
}

export interface ResourceInventory {
  id: string;
  depot_id: string;
  resource_type: string;
  quantity: number;
  reserved_quantity: number;
  unit: string;
  minimum_threshold: number;
  cost_per_unit: number;
  expiry_date: string | null;
  batch_number: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  available_quantity: number;
}

export interface ResourceInventoryCreate {
  depot_id: string;
  resource_type: string;
  quantity?: number;
  reserved_quantity?: number;
  unit?: string;
  minimum_threshold?: number;
  cost_per_unit?: number;
  expiry_date?: string;
  batch_number?: string;
  notes?: string;
}

export interface ResourceInventoryUpdate {
  quantity?: number;
  reserved_quantity?: number;
  minimum_threshold?: number;
  cost_per_unit?: number;
  expiry_date?: string;
  batch_number?: string;
  notes?: string;
}

export interface ResourceMovement {
  id: string;
  inventory_id: string;
  movement_type: string;
  quantity: number;
  from_depot_id: string | null;
  to_depot_id: string | null;
  mission_id: string | null;
  reference_number: string | null;
  notes: string | null;
  created_at: string;
}

export interface ResourceMovementCreate {
  inventory_id: string;
  movement_type: string;
  quantity: number;
  from_depot_id?: string;
  to_depot_id?: string;
  mission_id?: string;
  reference_number?: string;
  notes?: string;
}

export interface Personnel {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  role: string;
  skills: string | null;
  availability: boolean;
  depot_id: string | null;
  current_assignment: string | null;
  deployment_status: string;
  certifications: string | null;
  emergency_contact: string | null;
  emergency_phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonnelCreate {
  name: string;
  email?: string;
  phone?: string;
  role: string;
  skills?: string;
  availability?: boolean;
  depot_id?: string;
  current_assignment?: string;
  deployment_status?: string;
  certifications?: string;
  emergency_contact?: string;
  emergency_phone?: string;
}

export interface PersonnelUpdate {
  name?: string;
  email?: string;
  phone?: string;
  role?: string;
  skills?: string;
  availability?: boolean;
  depot_id?: string;
  current_assignment?: string;
  deployment_status?: string;
  certifications?: string;
  emergency_contact?: string;
  emergency_phone?: string;
}

export interface DemandPrediction {
  id: string;
  zone_id: string;
  resource_type: string;
  predicted_quantity: number;
  lower_bound: number | null;
  upper_bound: number | null;
  confidence_level: number | null;
  method: string;
  model_version: string | null;
  input_factors: string | null;
  vulnerability_adjustment: number;
  prediction_timestamp: string;
  created_at: string;
}

export interface DemandPredictionCreate {
  zone_id: string;
  resource_type: string;
  predicted_quantity: number;
  lower_bound?: number;
  upper_bound?: number;
  confidence_level?: number;
  method: string;
  model_version?: string;
  input_factors?: string;
  vulnerability_adjustment?: number;
}

export interface DemandPredictionRequest {
  incident_id: string;
  zone_ids?: string[];
  vulnerability_adjustment?: number;
}

export interface ResourceAllocation {
  id: string;
  zone_id: string;
  resource_type: string;
  allocated_quantity: number;
  fulfilled_quantity: number;
  source_depot_id: string | null;
  priority: number;
  status: string;
  notes: string | null;
  approved: boolean;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResourceAllocationCreate {
  zone_id: string;
  resource_type: string;
  allocated_quantity?: number;
  source_depot_id?: string;
  priority?: number;
  notes?: string;
}

export interface ResourceAllocationUpdate {
  allocated_quantity?: number;
  fulfilled_quantity?: number;
  source_depot_id?: string;
  priority?: number;
  status?: string;
  notes?: string;
  approved?: boolean;
  approved_by?: string;
}

export interface AllocationOptimizeRequest {
  incident_id: string;
  priority_overrides?: Record<string, number>;
  transport_capacity?: Record<string, number>;
}

export interface AllocationOptimizeResponse {
  allocation_plan_id: string;
  recommendations: ResourceAllocation[];
  unmet_demand: any[];
  unallocated_inventory: any[];
  coverage_summary: Record<string, any>;
  optimization_status: string;
  message: string | null;
}

export interface Mission {
  id: string;
  name: string;
  description: string | null;
  incident_id: string | null;
  zone_id: string | null;
  depot_id: string | null;
  destination_depot_id: string | null;
  status: string;
  priority: number;
  departure_time: string | null;
  estimated_arrival: string | null;
  actual_arrival: string | null;
  completion_time: string | null;
  route_distance_km: number | null;
  estimated_duration_hours: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  supply_manifest: MissionSupplyManifest[];
}

export interface MissionSupplyManifest {
  id: string;
  mission_id: string;
  resource_type: string;
  quantity: number;
  unit: string;
  loaded: boolean;
  delivered: boolean;
  notes: string | null;
}

export interface MissionCreate {
  name: string;
  description?: string;
  incident_id?: string;
  zone_id?: string;
  depot_id?: string;
  destination_depot_id?: string;
  priority?: number;
  supply_manifest?: MissionSupplyManifestCreate[];
}

export interface MissionSupplyManifestCreate {
  resource_type: string;
  quantity: number;
  unit?: string;
  notes?: string;
}

export interface MissionUpdate {
  name?: string;
  description?: string;
  incident_id?: string;
  zone_id?: string;
  depot_id?: string;
  destination_depot_id?: string;
  status?: string;
  priority?: number;
  departure_time?: string;
  estimated_arrival?: string;
  actual_arrival?: string;
  completion_time?: string;
  route_distance_km?: number;
  estimated_duration_hours?: number;
  notes?: string;
}

export interface MissionPersonnel {
  id: string;
  mission_id: string;
  personnel_id: string;
  role: string | null;
  assigned_at: string;
  personnel: Personnel;
}

export interface MissionPersonnelCreate {
  personnel_id: string;
  role?: string;
}

export interface FieldReport {
  id: string;
  mission_id: string;
  submitted_by: string | null;
  report_type: string;
  content: string;
  location: Coordinates | null;
  people_assisted: number;
  resources_delivered: string | null;
  issues: string | null;
  created_at: string;
  submitter: Personnel | null;
}

export interface FieldReportCreate {
  report_type?: string;
  content: string;
  longitude?: number;
  latitude?: number;
  people_assisted?: number;
  resources_delivered?: string;
  issues?: string;
}

export interface DataSourceRecord {
  id: string;
  source_name: string;
  source_type: string | null;
  incident_id: string | null;
  external_id: string | null;
  processed: boolean;
  processing_status: string;
  error_message: string | null;
  retrieved_at: string;
  processed_at: string | null;
}

export interface DataSource {
  id: string;
  name: string;
  type: string;
  url: string;
  description: string;
  enabled: boolean;
  last_sync: string | null;
  status: string;
}

export interface DashboardSummary {
  total_active_incidents: number;
  critical_incidents: number;
  high_incidents: number;
  resources_available: number;
  resources_deployed: number;
  active_personnel: number;
  people_affected: number;
  people_assisted: number;
}

export interface DashboardActivity {
  recent_incidents: Incident[];
  recent_missions: Mission[];
  high_priority_alerts: any[];
}

export interface AnalyticsSummary {
  total_incidents: number;
  total_resources_allocated: number;
  total_resources_delivered: number;
  total_people_affected: number;
  total_people_assisted: number;
  average_response_time_hours: number | null;
  mission_completion_rate: number;
  unmet_demand_by_type: Record<string, number>;
}