from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import AffectedZone, DemandPrediction, ResourceAllocation, ZoneSeverityEnum
from app.database.schemas import (
    AffectedZoneCreate, AffectedZoneUpdate, AffectedZoneResponse,
    DemandPredictionResponse, ResourceAllocationResponse
)

router = APIRouter()


@router.get("", response_model=List[AffectedZoneResponse])
async def list_zones(
    incident_id: Optional[UUID] = None,
    severity: Optional[ZoneSeverityEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AffectedZone)

    if incident_id:
        query = query.filter(AffectedZone.incident_id == incident_id)
    if severity:
        query = query.filter(AffectedZone.severity == severity)

    zones = query.order_by(desc(AffectedZone.created_at)).all()
    return zones


@router.get("/{zone_id}", response_model=AffectedZoneResponse)
async def get_zone(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.patch("/{zone_id}", response_model=AffectedZoneResponse)
async def update_zone(zone_id: UUID, update: AffectedZoneUpdate, db: Session = Depends(get_db)):
    zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(zone, field, value)

    zone.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/{zone_id}/predictions", response_model=List[DemandPredictionResponse])
async def get_zone_predictions(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    predictions = db.query(DemandPrediction).filter(DemandPrediction.zone_id == zone_id).all()
    return predictions


@router.get("/{zone_id}/allocations", response_model=List[ResourceAllocationResponse])
async def get_zone_allocations(zone_id: UUID, db: Session = Depends(get_db)):
    zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    allocations = db.query(ResourceAllocation).filter(ResourceAllocation.zone_id == zone_id).all()
    return allocations