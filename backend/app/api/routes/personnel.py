from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import Personnel, PersonnelRoleEnum
from app.database.schemas import PersonnelCreate, PersonnelUpdate, PersonnelResponse

router = APIRouter()


@router.get("", response_model=List[PersonnelResponse])
async def list_personnel(
    role: Optional[PersonnelRoleEnum] = None,
    depot_id: Optional[UUID] = None,
    availability: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Personnel)

    if role:
        query = query.filter(Personnel.role == role)
    if depot_id:
        query = query.filter(Personnel.depot_id == depot_id)
    if availability is not None:
        query = query.filter(Personnel.availability == availability)
    if search:
        query = query.filter(or_(
            Personnel.name.ilike(f"%{search}%"),
            Personnel.email.ilike(f"%{search}%"),
            Personnel.skills.ilike(f"%{search}%")
        ))

    personnel = query.order_by(Personnel.name).all()
    return personnel


@router.post("", response_model=PersonnelResponse, status_code=201)
async def create_personnel(personnel: PersonnelCreate, db: Session = Depends(get_db)):
    if personnel.email:
        existing = db.query(Personnel).filter(Personnel.email == personnel.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    if personnel.depot_id:
        from app.database.models import ResourceDepot
        depot = db.query(ResourceDepot).filter(ResourceDepot.id == personnel.depot_id).first()
        if not depot:
            raise HTTPException(status_code=404, detail="Depot not found")

    db_personnel = Personnel(**personnel.model_dump())
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.get("/{personnel_id}", response_model=PersonnelResponse)
async def get_personnel(personnel_id: UUID, db: Session = Depends(get_db)):
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return personnel


@router.patch("/{personnel_id}", response_model=PersonnelResponse)
async def update_personnel(personnel_id: UUID, update: PersonnelUpdate, db: Session = Depends(get_db)):
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")

    update_data = update.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"]:
        existing = db.query(Personnel).filter(
            Personnel.email == update_data["email"],
            Personnel.id != personnel_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    if "depot_id" in update_data and update_data["depot_id"]:
        from app.database.models import ResourceDepot
        depot = db.query(ResourceDepot).filter(ResourceDepot.id == update_data["depot_id"]).first()
        if not depot:
            raise HTTPException(status_code=404, detail="Depot not found")

    for field, value in update_data.items():
        setattr(personnel, field, value)

    personnel.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(personnel)
    return personnel


@router.delete("/{personnel_id}", status_code=204)
async def delete_personnel(personnel_id: UUID, db: Session = Depends(get_db)):
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")

    db.delete(personnel)
    db.commit()