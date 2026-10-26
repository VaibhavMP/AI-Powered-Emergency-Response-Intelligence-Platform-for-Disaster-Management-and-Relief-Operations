from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import ResourceDepot, ResourceInventory, ResourceMovement, ResourceTypeEnum
from app.database.schemas import (
    ResourceDepotCreate, ResourceDepotUpdate, ResourceDepotResponse,
    ResourceInventoryCreate, ResourceInventoryUpdate, ResourceInventoryResponse,
    ResourceMovementCreate, ResourceMovementResponse
)

router = APIRouter()


@router.get("", response_model=List[ResourceDepotResponse])
async def list_depots(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ResourceDepot)
    if is_active is not None:
        query = query.filter(ResourceDepot.is_active == is_active)
    depots = query.order_by(ResourceDepot.name).all()
    return depots


@router.post("", response_model=ResourceDepotResponse, status_code=201)
async def create_depot(depot: ResourceDepotCreate, db: Session = Depends(get_db)):
    db_depot = ResourceDepot(
        name=depot.name,
        longitude=depot.longitude,
        latitude=depot.latitude,
        address=depot.address,
        contact_person=depot.contact_person,
        contact_phone=depot.contact_phone,
        capacity=depot.capacity,
        is_active=depot.is_active
    )
    db.add(db_depot)
    db.commit()
    db.refresh(db_depot)
    return db_depot


@router.get("/{depot_id}", response_model=ResourceDepotResponse)
async def get_depot(depot_id: UUID, db: Session = Depends(get_db)):
    depot = db.query(ResourceDepot).filter(ResourceDepot.id == depot_id).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")
    return depot


@router.patch("/{depot_id}", response_model=ResourceDepotResponse)
async def update_depot(depot_id: UUID, update: ResourceDepotUpdate, db: Session = Depends(get_db)):
    depot = db.query(ResourceDepot).filter(ResourceDepot.id == depot_id).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")

    update_data = update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(depot, field, value)

    depot.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(depot)
    return depot


@router.get("/{depot_id}/inventory", response_model=List[ResourceInventoryResponse])
async def get_depot_inventory(depot_id: UUID, db: Session = Depends(get_db)):
    depot = db.query(ResourceDepot).filter(ResourceDepot.id == depot_id).first()
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")

    inventory = db.query(ResourceInventory).filter(ResourceInventory.depot_id == depot_id).all()
    result = []
    for item in inventory:
        item_dict = item.__dict__.copy()
        item_dict['available_quantity'] = item.quantity - item.reserved_quantity
        result.append(ResourceInventoryResponse(**item_dict))
    return result