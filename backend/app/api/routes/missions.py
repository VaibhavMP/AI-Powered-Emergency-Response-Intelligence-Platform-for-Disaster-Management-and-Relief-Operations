from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import (
    Mission, MissionSupplyManifest, MissionPersonnel, FieldReport,
    Personnel, ResourceDepot, AffectedZone, Incident,
    MissionStatusEnum, ResourceTypeEnum
)
from app.database.schemas import (
    MissionCreate, MissionUpdate, MissionResponse,
    MissionSupplyManifestCreate, MissionSupplyManifestResponse,
    MissionPersonnelCreate, MissionPersonnelResponse,
    FieldReportCreate, FieldReportResponse
)

router = APIRouter()


@router.get("", response_model=List[MissionResponse])
async def list_missions(
    status: Optional[MissionStatusEnum] = None,
    incident_id: Optional[UUID] = None,
    zone_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Mission)

    if status:
        query = query.filter(Mission.status == status)
    if incident_id:
        query = query.filter(Mission.incident_id == incident_id)
    if zone_id:
        query = query.filter(Mission.zone_id == zone_id)

    missions = query.order_by(desc(Mission.created_at)).all()
    return missions


@router.post("", response_model=MissionResponse, status_code=201)
async def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    if mission.incident_id:
        incident = db.query(Incident).filter(Incident.id == mission.incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

    if mission.zone_id:
        zone = db.query(AffectedZone).filter(AffectedZone.id == mission.zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail="Zone not found")

    if mission.depot_id:
        depot = db.query(ResourceDepot).filter(ResourceDepot.id == mission.depot_id).first()
        if not depot:
            raise HTTPException(status_code=404, detail="Source depot not found")

    if mission.destination_depot_id:
        depot = db.query(ResourceDepot).filter(ResourceDepot.id == mission.destination_depot_id).first()
        if not depot:
            raise HTTPException(status_code=404, detail="Destination depot not found")

    db_mission = Mission(
        name=mission.name,
        description=mission.description,
        incident_id=mission.incident_id,
        zone_id=mission.zone_id,
        depot_id=mission.depot_id,
        destination_depot_id=mission.destination_depot_id,
        priority=mission.priority,
        status=MissionStatusEnum.pending
    )
    db.add(db_mission)
    db.flush()

    for item in mission.supply_manifest:
        manifest_item = MissionSupplyManifest(
            mission_id=db_mission.id,
            resource_type=item.resource_type,
            quantity=item.quantity,
            unit=item.unit,
            notes=item.notes
        )
        db.add(manifest_item)

    db.commit()
    db.refresh(db_mission)
    return db_mission


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: UUID, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.patch("/{mission_id}", response_model=MissionResponse)
async def update_mission(mission_id: UUID, update: MissionUpdate, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    update_data = update.model_dump(exclude_unset=True)

    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == MissionStatusEnum.in_progress and not mission.departure_time:
            mission.departure_time = datetime.utcnow()
        elif new_status == MissionStatusEnum.completed and not mission.completion_time:
            mission.completion_time = datetime.utcnow()

    for field, value in update_data.items():
        setattr(mission, field, value)

    mission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(mission)
    return mission


@router.post("/{mission_id}/personnel", response_model=MissionPersonnelResponse, status_code=201)
async def assign_personnel(mission_id: UUID, assignment: MissionPersonnelCreate, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    personnel = db.query(Personnel).filter(Personnel.id == assignment.personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")

    existing = db.query(MissionPersonnel).filter(
        MissionPersonnel.mission_id == mission_id,
        MissionPersonnel.personnel_id == assignment.personnel_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Personnel already assigned to this mission")

    db_assignment = MissionPersonnel(
        mission_id=mission_id,
        personnel_id=assignment.personnel_id,
        role=assignment.role
    )
    db.add(db_assignment)

    personnel.current_assignment = mission.name
    personnel.deployment_status = "deployed"

    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@router.get("/{mission_id}/personnel", response_model=List[MissionPersonnelResponse])
async def get_mission_personnel(mission_id: UUID, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    assignments = db.query(MissionPersonnel).filter(MissionPersonnel.mission_id == mission_id).all()
    return assignments


@router.post("/{mission_id}/reports", response_model=FieldReportResponse, status_code=201)
async def submit_field_report(mission_id: UUID, report: FieldReportCreate, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    db_report = FieldReport(
        mission_id=mission_id,
        report_type=report.report_type,
        content=report.content,
        longitude=report.longitude,
        latitude=report.latitude,
        people_assisted=report.people_assisted,
        resources_delivered=report.resources_delivered,
        issues=report.issues
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/{mission_id}/reports", response_model=List[FieldReportResponse])
async def get_mission_reports(mission_id: UUID, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    reports = db.query(FieldReport).filter(FieldReport.mission_id == mission_id).order_by(desc(FieldReport.created_at)).all()
    return reports