from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.database.models import (
    Incident, AffectedZone, ResourceInventory, ResourceMovement,
    Mission, FieldReport, DemandPrediction, ResourceAllocation,
    Personnel, ResourceTypeEnum, MissionStatusEnum, IncidentStatusEnum, SeverityEnum
)
from app.database.schemas import AnalyticsSummary

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)

    total_incidents = db.query(func.count(Incident.id)).filter(Incident.created_at >= since).scalar() or 0

    total_allocated = db.query(func.sum(ResourceAllocation.allocated_quantity)).scalar() or 0

    total_delivered = db.query(func.sum(ResourceMovement.quantity)).filter(
        ResourceMovement.movement_type == "dispatch",
        ResourceMovement.created_at >= since
    ).scalar() or 0

    total_affected = db.query(func.sum(AffectedZone.affected_population)).scalar() or 0

    total_assisted = db.query(func.sum(FieldReport.people_assisted)).filter(
        FieldReport.created_at >= since
    ).scalar() or 0

    completed_missions_list = db.query(Mission).filter(
        Mission.status == MissionStatusEnum.completed,
        Mission.departure_time.isnot(None),
        Mission.completion_time.isnot(None),
        Mission.created_at >= since
    ).all()
    if completed_missions_list:
        durations = [(m.completion_time - m.departure_time).total_seconds() / 3600 for m in completed_missions_list if m.completion_time and m.departure_time]
        avg_response = sum(durations) / len(durations) if durations else None
    else:
        avg_response = None

    completed_missions = db.query(func.count(Mission.id)).filter(
        Mission.status == MissionStatusEnum.completed,
        Mission.created_at >= since
    ).scalar() or 0

    total_missions = db.query(func.count(Mission.id)).filter(Mission.created_at >= since).scalar() or 1
    completion_rate = (completed_missions / total_missions * 100) if total_missions > 0 else 0

    unmet_demand = {}
    for rt in ResourceTypeEnum:
        demand = db.query(func.sum(DemandPrediction.predicted_quantity)).filter(
            DemandPrediction.resource_type == rt
        ).scalar() or 0
        allocated = db.query(func.sum(ResourceAllocation.allocated_quantity)).filter(
            ResourceAllocation.resource_type == rt
        ).scalar() or 0
        unmet_demand[rt.value] = max(0, demand - allocated)

    return AnalyticsSummary(
        total_incidents=total_incidents,
        total_resources_allocated=total_allocated,
        total_resources_delivered=total_delivered,
        total_people_affected=total_affected,
        total_people_assisted=total_assisted,
        average_response_time_hours=round(avg_response, 2) if avg_response else None,
        mission_completion_rate=round(completion_rate, 1),
        unmet_demand_by_type=unmet_demand
    )


@router.get("/resource-demand")
async def get_resource_demand_analytics(
    incident_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        DemandPrediction.resource_type,
        func.sum(DemandPrediction.predicted_quantity).label('total_demand'),
        func.sum(DemandPrediction.lower_bound).label('total_lower'),
        func.sum(DemandPrediction.upper_bound).label('total_upper')
    ).group_by(DemandPrediction.resource_type)

    if incident_id:
        query = query.join(AffectedZone).filter(AffectedZone.incident_id == incident_id)

    results = query.all()

    demand_data = []
    for row in results:
        allocated = db.query(func.sum(ResourceAllocation.allocated_quantity)).filter(
            ResourceAllocation.resource_type == row.resource_type
        ).scalar() or 0

        available = db.query(func.sum(ResourceInventory.quantity - ResourceInventory.reserved_quantity)).filter(
            ResourceInventory.resource_type == row.resource_type
        ).scalar() or 0

        demand_data.append({
            "resource_type": row.resource_type.value,
            "predicted_demand": row.total_demand,
            "lower_bound": row.total_lower,
            "upper_bound": row.total_upper,
            "allocated": allocated,
            "available_inventory": available,
            "shortage": max(0, row.total_demand - allocated)
        })

    return demand_data


@router.get("/incident-history")
async def get_incident_history(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)

    incidents = db.query(Incident).filter(Incident.created_at >= since).order_by(Incident.created_at).all()

    by_type = {}
    by_severity = {}
    by_month = {}

    for inc in incidents:
        by_type[inc.disaster_type.value] = by_type.get(inc.disaster_type.value, 0) + 1
        by_severity[inc.severity.value] = by_severity.get(inc.severity.value, 0) + 1
        month_key = inc.created_at.strftime("%Y-%m")
        by_month[month_key] = by_month.get(month_key, 0) + 1

    return {
        "by_type": by_type,
        "by_severity": by_severity,
        "by_month": by_month,
        "total": len(incidents)
    }