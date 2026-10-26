from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import Incident, AffectedZone, DataSourceRecord, IncidentStatusEnum, DisasterTypeEnum, SeverityEnum
from app.database.schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, IncidentListResponse,
    AffectedZoneCreate, AffectedZoneUpdate, AffectedZoneResponse,
    DataSourceRecordResponse
)

router = APIRouter()


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[IncidentStatusEnum] = None,
    disaster_type: Optional[DisasterTypeEnum] = None,
    severity: Optional[SeverityEnum] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if disaster_type:
        query = query.filter(Incident.disaster_type == disaster_type)
    if severity:
        query = query.filter(Incident.severity == severity)
    if search:
        query = query.filter(or_(
            Incident.name.ilike(f"%{search}%"),
            Incident.description.ilike(f"%{search}%")
        ))

    total = query.count()
    incidents = query.order_by(desc(Incident.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return IncidentListResponse(
        items=incidents,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(
        name=incident.name,
        disaster_type=incident.disaster_type,
        severity=incident.severity,
        description=incident.description,
        longitude=incident.longitude,
        latitude=incident.latitude,
        affected_population=incident.affected_population,
        estimated_affected_population=incident.estimated_affected_population,
        reported_by=incident.reported_by,
        source_id=incident.source_id,
        external_id=incident.external_id,
        status=IncidentStatusEnum.active
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: UUID, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: UUID, update: IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(incident, field, value)

    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/{incident_id}", status_code=204)
async def delete_incident(incident_id: UUID, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status not in [IncidentStatusEnum.closed, IncidentStatusEnum.recovered]:
        raise HTTPException(status_code=400, detail="Only closed or recovered incidents can be deleted")

    db.delete(incident)
    db.commit()


@router.get("/{incident_id}/zones", response_model=List[AffectedZoneResponse])
async def get_incident_zones(incident_id: UUID, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    zones = db.query(AffectedZone).filter(AffectedZone.incident_id == incident_id).all()
    return zones


@router.post("/{incident_id}/zones", response_model=AffectedZoneResponse, status_code=201)
async def create_zone(incident_id: UUID, zone: AffectedZoneCreate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    db_zone = AffectedZone(
        incident_id=incident_id,
        name=zone.name,
        centroid_longitude=zone.centroid_longitude,
        centroid_latitude=zone.centroid_latitude,
        severity=zone.severity,
        affected_population=zone.affected_population,
        vulnerable_children=zone.vulnerable_children,
        vulnerable_elderly=zone.vulnerable_elderly,
        vulnerable_medical=zone.vulnerable_medical,
        buildings_damaged=zone.buildings_damaged,
        buildings_destroyed=zone.buildings_destroyed,
        infrastructure_damage=zone.infrastructure_damage,
        assessment_notes=zone.assessment_notes
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone