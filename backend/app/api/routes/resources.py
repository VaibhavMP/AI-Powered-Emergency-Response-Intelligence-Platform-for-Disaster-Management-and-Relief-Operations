from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import ResourceInventory, ResourceMovement, ResourceDepot, ResourceTypeEnum
from app.database.schemas import (
    ResourceInventoryCreate, ResourceInventoryUpdate, ResourceInventoryResponse,
    ResourceMovementCreate, ResourceMovementResponse
)

router = APIRouter()


@router.get("", response_model=List[ResourceInventoryResponse])
async def list_resources(
    resource_type: Optional[ResourceTypeEnum] = None,
    depot_id: Optional[UUID] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(ResourceInventory).join(ResourceDepot)

    if resource_type:
        query = query.filter(ResourceInventory.resource_type == resource_type)
    if depot_id:
        query = query.filter(ResourceInventory.depot_id == depot_id)
    if low_stock_only:
        query = query.filter(
            (ResourceInventory.quantity - ResourceInventory.reserved_quantity) <= ResourceInventory.minimum_threshold
        )

    inventory = query.order_by(ResourceInventory.resource_type, ResourceDepot.name).all()

    result = []
    for item in inventory:
        item_dict = item.__dict__.copy()
        item_dict['available_quantity'] = item.quantity - item.reserved_quantity
        result.append(ResourceInventoryResponse(**item_dict))
    return result


@router.post("", response_model=ResourceInventoryResponse, status_code=201)
async def create_resource(inventory: ResourceInventoryCreate, db: Session = Depends(get_db)):
    depot = db.query(ResourceDepot).filter(ResourceDepot.id == inventory.depot_id).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")

    existing = db.query(ResourceInventory).filter(
        ResourceInventory.depot_id == inventory.depot_id,
        ResourceInventory.resource_type == inventory.resource_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Resource type already exists at this depot")

    db_inventory = ResourceInventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)

    item_dict = db_inventory.__dict__.copy()
    item_dict['available_quantity'] = db_inventory.quantity - db_inventory.reserved_quantity
    return ResourceInventoryResponse(**item_dict)


@router.patch("/{inventory_id}", response_model=ResourceInventoryResponse)
async def update_resource(inventory_id: UUID, update: ResourceInventoryUpdate, db: Session = Depends(get_db)):
    inventory = db.query(ResourceInventory).filter(ResourceInventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    update_data = update.model_dump(exclude_unset=True)

    if "reserved_quantity" in update_data and update_data["reserved_quantity"] > inventory.quantity:
        raise HTTPException(status_code=400, detail="Reserved quantity cannot exceed total quantity")

    for field, value in update_data.items():
        setattr(inventory, field, value)

    inventory.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(inventory)

    item_dict = inventory.__dict__.copy()
    item_dict['available_quantity'] = inventory.quantity - inventory.reserved_quantity
    return ResourceInventoryResponse(**item_dict)


@router.post("/dispatch", response_model=ResourceMovementResponse)
async def dispatch_resource(dispatch: ResourceMovementCreate, db: Session = Depends(get_db)):
    inventory = db.query(ResourceInventory).filter(ResourceInventory.id == dispatch.inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    available = inventory.quantity - inventory.reserved_quantity
    if dispatch.quantity > available:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {available}, Requested: {dispatch.quantity}")

    if dispatch.from_depot_id and dispatch.from_depot_id != inventory.depot_id:
        raise HTTPException(status_code=400, detail="Source depot does not match inventory depot")

    inventory.reserved_quantity += dispatch.quantity

    movement = ResourceMovement(
        inventory_id=dispatch.inventory_id,
        movement_type="dispatch",
        quantity=dispatch.quantity,
        from_depot_id=dispatch.from_depot_id or inventory.depot_id,
        to_depot_id=dispatch.to_depot_id,
        mission_id=dispatch.mission_id,
        reference_number=dispatch.reference_number,
        notes=dispatch.notes
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.post("/receive", response_model=ResourceMovementResponse)
async def receive_resource(receive: ResourceMovementCreate, db: Session = Depends(get_db)):
    inventory = db.query(ResourceInventory).filter(ResourceInventory.id == receive.inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if receive.to_depot_id and receive.to_depot_id != inventory.depot_id:
        raise HTTPException(status_code=400, detail="Destination depot does not match inventory depot")

    inventory.quantity += receive.quantity

    movement = ResourceMovement(
        inventory_id=receive.inventory_id,
        movement_type="receive",
        quantity=receive.quantity,
        from_depot_id=receive.from_depot_id,
        to_depot_id=receive.to_depot_id or inventory.depot_id,
        mission_id=receive.mission_id,
        reference_number=receive.reference_number,
        notes=receive.notes
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/movements", response_model=List[ResourceMovementResponse])
async def list_movements(
    inventory_id: Optional[UUID] = None,
    mission_id: Optional[UUID] = None,
    movement_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(ResourceMovement)

    if inventory_id:
        query = query.filter(ResourceMovement.inventory_id == inventory_id)
    if mission_id:
        query = query.filter(ResourceMovement.mission_id == mission_id)
    if movement_type:
        query = query.filter(ResourceMovement.movement_type == movement_type)

    movements = query.order_by(desc(ResourceMovement.created_at)).limit(limit).all()
    return movements