from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import (
    ResourceAllocation, AffectedZone, ResourceInventory, ResourceDepot,
    ResourceTypeEnum, Incident, DemandPrediction
)
from app.database.schemas import (
    ResourceAllocationCreate, ResourceAllocationUpdate, ResourceAllocationResponse,
    AllocationOptimizeRequest, AllocationOptimizeResponse
)

router = APIRouter()


@router.post("/optimize", response_model=AllocationOptimizeResponse)
async def optimize_allocation(request: AllocationOptimizeRequest, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    zones = db.query(AffectedZone).filter(AffectedZone.incident_id == request.incident_id).all()
    if not zones:
        raise HTTPException(status_code=404, detail="No zones found for this incident")

    all_inventory = db.query(ResourceInventory).join(ResourceDepot).filter(
        ResourceDepot.is_active == True
    ).all()

    inventory_by_type = {}
    for item in all_inventory:
        key = item.resource_type
        if key not in inventory_by_type:
            inventory_by_type[key] = []
        available = item.quantity - item.reserved_quantity
        if available > 0:
            inventory_by_type[key].append({
                "depot_id": item.depot_id,
                "inventory_id": item.id,
                "available": available
            })

    recommendations = []
    unmet_demand = []
    unallocated_inventory = {rt: sum(i["available"] for i in items) for rt, items in inventory_by_type.items()}

    priority_overrides = request.priority_overrides or {}

    for zone in zones:
        zone_priority = priority_overrides.get(str(zone.id), 0)
        severity_priority = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(zone.severity.value, 1)
        total_priority = zone_priority + severity_priority

        zone_predictions = db.query(DemandPrediction).filter(DemandPrediction.zone_id == zone.id).all()
        if not zone_predictions:
            continue

        for pred in zone_predictions:
            rt = pred.resource_type
            demand = pred.predicted_quantity
            available_items = inventory_by_type.get(rt, [])

            total_available = sum(i["available"] for i in available_items)
            allocated = min(demand, total_available)

            if allocated > 0:
                for item in available_items:
                    if allocated <= 0:
                        break
                    take = min(item["available"], allocated)
                    alloc = ResourceAllocation(
                        zone_id=zone.id,
                        resource_type=rt,
                        allocated_quantity=take,
                        source_depot_id=item["depot_id"],
                        priority=total_priority,
                        status="planned"
                    )
                    db.add(alloc)
                    recommendations.append(alloc)
                    item["available"] -= take
                    allocated -= take
                    unallocated_inventory[rt] = unallocated_inventory.get(rt, 0) - take

            unmet = demand - sum(r.allocated_quantity for r in recommendations if r.zone_id == zone.id and r.resource_type == rt)
            if unmet > 0:
                unmet_demand.append({
                    "zone_id": str(zone.id),
                    "zone_name": zone.name,
                    "resource_type": rt.value,
                    "demand": demand,
                    "allocated": demand - unmet,
                    "unmet": unmet
                })

    db.commit()
    for r in recommendations:
        db.refresh(r)

    coverage = {}
    for zone in zones:
        zone_allocs = [r for r in recommendations if r.zone_id == zone.id]
        total_demand = sum(p.predicted_quantity for z in [zone] for p in db.query(DemandPrediction).filter(DemandPrediction.zone_id == z.id).all())
        total_allocated = sum(a.allocated_quantity for a in zone_allocs)
        coverage[str(zone.id)] = {
            "zone_name": zone.name,
            "coverage_pct": round((total_allocated / total_demand * 100) if total_demand > 0 else 100, 1),
            "total_demand": total_demand,
            "total_allocated": total_allocated
        }

    return AllocationOptimizeResponse(
        allocation_plan_id=recommendations[0].id if recommendations else UUID(int=0),
        recommendations=recommendations,
        unmet_demand=unmet_demand,
        unallocated_inventory=[{"resource_type": k, "quantity": v} for k, v in unallocated_inventory.items() if v > 0],
        coverage_summary=coverage,
        optimization_status="completed",
        message="Baseline greedy allocation completed. For optimal results, integrate OR-Tools."
    )


@router.get("", response_model=List[ResourceAllocationResponse])
async def list_allocations(
    zone_id: Optional[UUID] = None,
    resource_type: Optional[ResourceTypeEnum] = None,
    approved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ResourceAllocation)

    if zone_id:
        query = query.filter(ResourceAllocation.zone_id == zone_id)
    if resource_type:
        query = query.filter(ResourceAllocation.resource_type == resource_type)
    if approved is not None:
        query = query.filter(ResourceAllocation.approved == approved)

    allocations = query.order_by(desc(ResourceAllocation.created_at)).all()
    return allocations


@router.post("/{allocation_id}/approve", response_model=ResourceAllocationResponse)
async def approve_allocation(allocation_id: UUID, db: Session = Depends(get_db)):
    allocation = db.query(ResourceAllocation).filter(ResourceAllocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if allocation.approved:
        raise HTTPException(status_code=400, detail="Allocation already approved")

    inventory = db.query(ResourceInventory).filter(
        ResourceInventory.depot_id == allocation.source_depot_id,
        ResourceInventory.resource_type == allocation.resource_type
    ).first()

    if not inventory:
        raise HTTPException(status_code=400, detail="Source inventory not found")

    available = inventory.quantity - inventory.reserved_quantity
    if allocation.allocated_quantity > available:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {available}")

    inventory.reserved_quantity += allocation.allocated_quantity
    allocation.approved = True
    allocation.approved_at = datetime.utcnow()
    allocation.status = "approved"

    db.commit()
    db.refresh(allocation)
    return allocation