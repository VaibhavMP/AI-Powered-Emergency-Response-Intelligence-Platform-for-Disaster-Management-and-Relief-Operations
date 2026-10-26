from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import csv
import io
from fastapi.responses import StreamingResponse

from app.database.connection import get_db
from app.database.models import (
    Incident, AffectedZone, ResourceInventory, ResourceMovement,
    Mission, FieldReport, DemandPrediction, ResourceAllocation,
    Personnel, ResourceTypeEnum, MissionStatusEnum, IncidentStatusEnum, SeverityEnum
)
from app.database.schemas import SituationReport

router = APIRouter()


@router.get("")
@router.get("/situation")
async def generate_situation_report(
    incident_id: Optional[UUID] = None,
    days: int = Query(7, ge=1, le=30),
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)

    query = db.query(Incident)
    if incident_id:
        query = query.filter(Incident.id == incident_id)
    incidents = query.filter(Incident.created_at >= since).all()

    if not incidents and incident_id:
        raise HTTPException(status_code=404, detail="Incident not found")

    report_data = []
    for inc in incidents:
        zones = db.query(AffectedZone).filter(AffectedZone.incident_id == inc.id).all()
        zone_ids = [z.id for z in zones]

        allocations = db.query(ResourceAllocation).filter(ResourceAllocation.zone_id.in_(zone_ids)).all() if zone_ids else []
        movements = db.query(ResourceMovement).join(ResourceInventory).filter(
            ResourceInventory.depot_id.in_([z.incident_id for z in zones]) if zone_ids else [UUID(int=0)]
        ).all() if zone_ids else []

        missions = db.query(Mission).filter(Mission.incident_id == inc.id).all()
        reports = db.query(FieldReport).join(Mission).filter(Mission.incident_id == inc.id).all()

        resources_allocated = {}
        resources_delivered = {}
        for alloc in allocations:
            key = alloc.resource_type.value
            resources_allocated[key] = resources_allocated.get(key, 0) + alloc.allocated_quantity

        for mv in movements:
            if mv.movement_type == "dispatch":
                inv = db.query(ResourceInventory).filter(ResourceInventory.id == mv.inventory_id).first()
                if inv:
                    key = inv.resource_type.value
                    resources_delivered[key] = resources_delivered.get(key, 0) + mv.quantity

        demand_vs_supply = {}
        for rt in ResourceTypeEnum:
            demand = db.query(func.sum(DemandPrediction.predicted_quantity)).filter(
                DemandPrediction.zone_id.in_(zone_ids),
                DemandPrediction.resource_type == rt
            ).scalar() or 0 if zone_ids else 0
            allocated = resources_allocated.get(rt.value, 0)
            demand_vs_supply[rt.value] = {"demand": demand, "allocated": allocated, "gap": max(0, demand - allocated)}

        zone_coverage = {}
        for zone in zones:
            zone_allocs = [a for a in allocations if a.zone_id == zone.id]
            total_demand = db.query(func.sum(DemandPrediction.predicted_quantity)).filter(
                DemandPrediction.zone_id == zone.id
            ).scalar() or 0
            total_allocated = sum(a.allocated_quantity for a in zone_allocs)
            zone_coverage[zone.name] = {
                "severity": zone.severity.value,
                "population": zone.affected_population,
                "demand": total_demand,
                "allocated": total_allocated,
                "coverage_pct": round((total_allocated / total_demand * 100) if total_demand > 0 else 100, 1)
            }

        mission_stats = {
            "total": len(missions),
            "pending": len([m for m in missions if m.status == MissionStatusEnum.pending]),
            "in_progress": len([m for m in missions if m.status == MissionStatusEnum.in_progress]),
            "completed": len([m for m in missions if m.status == MissionStatusEnum.completed]),
            "cancelled": len([m for m in missions if m.status == MissionStatusEnum.cancelled])
        }

        unmet_demand = {}
        for rt in ResourceTypeEnum:
            demand = db.query(func.sum(DemandPrediction.predicted_quantity)).filter(
                DemandPrediction.zone_id.in_(zone_ids),
                DemandPrediction.resource_type == rt
            ).scalar() or 0 if zone_ids else 0
            allocated = resources_allocated.get(rt.value, 0)
            if demand > allocated:
                unmet_demand[rt.value] = demand - allocated

        recommendations = []
        if unmet_demand:
            recommendations.append(f"Critical shortages in: {', '.join(unmet_demand.keys())}")
        if mission_stats["pending"] > 0:
            recommendations.append(f"{mission_stats['pending']} missions awaiting assignment")
        if any(z.severity.value in ["critical", "high"] for z in zones):
            recommendations.append("High-priority zones require immediate resource deployment")

        incident_report = {
            "incident_id": str(inc.id),
            "incident_name": inc.name,
            "disaster_type": inc.disaster_type.value,
            "severity": inc.severity.value,
            "status": inc.status.value,
            "location": f"{inc.latitude:.4f}, {inc.longitude:.4f}" if (inc.latitude and inc.longitude) else "Unknown",
            "affected_population": sum(z.affected_population for z in zones),
            "resources_allocated": resources_allocated,
            "resources_delivered": resources_delivered,
            "demand_vs_supply": demand_vs_supply,
            "zone_coverage": zone_coverage,
            "mission_stats": mission_stats,
            "unmet_demand": unmet_demand,
            "recommendations": recommendations,
            "people_assisted": sum(r.people_assisted for r in reports)
        }
        report_data.append(incident_report)

    if format == "csv":
        return export_csv(report_data, since, datetime.utcnow())

    return {
        "report_id": UUID(int=0),
        "generated_at": datetime.utcnow(),
        "period_start": since,
        "period_end": datetime.utcnow(),
        "incidents": report_data
    }


def export_csv(report_data: list, period_start: datetime, period_end: datetime):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Disaster Response Situation Report"])
    writer.writerow(["Generated:", datetime.utcnow().isoformat()])
    writer.writerow(["Period:", period_start.isoformat(), "to", period_end.isoformat()])
    writer.writerow([])

    for inc in report_data:
        writer.writerow([f"Incident: {inc['incident_name']} ({inc['disaster_type']})"])
        writer.writerow(["Incident ID", "Severity", "Status", "Affected Population"])
        writer.writerow([inc['incident_id'], inc['severity'], inc['status'], inc['affected_population']])
        writer.writerow([])

        writer.writerow(["Resources Allocated"])
        writer.writerow(["Resource Type", "Quantity"])
        for rt, qty in inc['resources_allocated'].items():
            writer.writerow([rt, qty])
        writer.writerow([])

        writer.writerow(["Resources Delivered"])
        writer.writerow(["Resource Type", "Quantity"])
        for rt, qty in inc['resources_delivered'].items():
            writer.writerow([rt, qty])
        writer.writerow([])

        writer.writerow(["Demand vs Supply"])
        writer.writerow(["Resource Type", "Demand", "Allocated", "Gap"])
        for rt, data in inc['demand_vs_supply'].items():
            writer.writerow([rt, data['demand'], data['allocated'], data['gap']])
        writer.writerow([])

        writer.writerow(["Zone Coverage"])
        writer.writerow(["Zone", "Severity", "Population", "Demand", "Allocated", "Coverage %"])
        for zone, data in inc['zone_coverage'].items():
            writer.writerow([zone, data['severity'], data['population'], data['demand'], data['allocated'], data['coverage_pct']])
        writer.writerow([])

        writer.writerow(["Mission Statistics"])
        writer.writerow(["Status", "Count"])
        for status, count in inc['mission_stats'].items():
            writer.writerow([status, count])
        writer.writerow([])

        writer.writerow(["Unmet Demand"])
        writer.writerow(["Resource Type", "Unmet Quantity"])
        for rt, qty in inc['unmet_demand'].items():
            writer.writerow([rt, qty])
        writer.writerow([])

        writer.writerow(["Recommendations"])
        for rec in inc['recommendations']:
            writer.writerow([rec])
        writer.writerow([])
        writer.writerow([])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=situation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"}
    )