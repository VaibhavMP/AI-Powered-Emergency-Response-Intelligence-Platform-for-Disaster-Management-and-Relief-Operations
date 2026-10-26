from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.database.models import (
    Incident, AffectedZone, ResourceInventory, ResourceDepot,
    Personnel, Mission, ResourceAllocation, ResourceMovement,
    MissionSupplyManifest, FieldReport, IncidentStatusEnum,
    MissionStatusEnum, SeverityEnum
)
from app.database.schemas import (
    DashboardSummary, DashboardActivity, IncidentResponse,
    MissionResponse
)

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    total_active = db.query(func.count(Incident.id)).filter(
        Incident.status.in_([IncidentStatusEnum.active, IncidentStatusEnum.monitoring])
    ).scalar() or 0

    critical_count = db.query(func.count(Incident.id)).filter(
        Incident.severity == SeverityEnum.critical,
        Incident.status.in_([IncidentStatusEnum.active, IncidentStatusEnum.monitoring])
    ).scalar() or 0

    high_count = db.query(func.count(Incident.id)).filter(
        Incident.severity == SeverityEnum.high,
        Incident.status.in_([IncidentStatusEnum.active, IncidentStatusEnum.monitoring])
    ).scalar() or 0

    total_available = db.query(func.sum(ResourceInventory.quantity - ResourceInventory.reserved_quantity)).scalar() or 0
    total_deployed = db.query(func.sum(ResourceMovement.quantity)).filter(
        ResourceMovement.movement_type == "dispatch"
    ).scalar() or 0

    active_personnel = db.query(func.count(Personnel.id)).filter(
        Personnel.availability == True,
        Personnel.deployment_status.in_(["available", "deployed"])
    ).scalar() or 0

    total_affected = db.query(func.sum(AffectedZone.affected_population)).scalar() or 0
    total_assisted = db.query(func.sum(FieldReport.people_assisted)).scalar() or 0

    return DashboardSummary(
        total_active_incidents=total_active,
        critical_incidents=critical_count,
        high_incidents=high_count,
        resources_available=max(0, total_available),
        resources_deployed=total_deployed,
        active_personnel=active_personnel,
        people_affected=total_affected,
        people_assisted=total_assisted
    )


@router.get("/activity", response_model=DashboardActivity)
async def get_dashboard_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    recent_incidents = db.query(Incident).order_by(
        desc(Incident.created_at)
    ).limit(limit).all()

    recent_missions = db.query(Mission).order_by(
        desc(Mission.created_at)
    ).limit(limit).all()

    active_critical = db.query(Incident).filter(
        Incident.severity == SeverityEnum.critical,
        Incident.status.in_([IncidentStatusEnum.active, IncidentStatusEnum.monitoring])
    ).order_by(desc(Incident.created_at)).limit(5).all()

    alerts = [
        {
            "type": "critical_incident",
            "incident_id": str(inc.id),
            "incident_name": inc.name,
            "severity": inc.severity.value,
            "message": f"Critical incident: {inc.name} ({inc.disaster_type.value})"
        }
        for inc in active_critical
    ]

    return DashboardActivity(
        recent_incidents=recent_incidents,
        recent_missions=recent_missions,
        high_priority_alerts=alerts
    )