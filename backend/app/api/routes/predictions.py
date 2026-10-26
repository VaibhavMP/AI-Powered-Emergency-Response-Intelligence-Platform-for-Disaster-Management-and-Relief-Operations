from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import DemandPrediction, AffectedZone, Incident, ResourceTypeEnum
from app.database.schemas import DemandPredictionCreate, DemandPredictionResponse, DemandPredictionRequest

router = APIRouter()


@router.post("", response_model=DemandPredictionResponse, status_code=201)
async def create_prediction(prediction: DemandPredictionCreate, db: Session = Depends(get_db)):
    zone = db.query(AffectedZone).filter(AffectedZone.id == prediction.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    db_prediction = DemandPrediction(**prediction.model_dump())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


@router.post("/predict", response_model=List[DemandPredictionResponse])
async def run_demand_prediction(request: DemandPredictionRequest, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    query = db.query(AffectedZone).filter(AffectedZone.incident_id == request.incident_id)
    if request.zone_ids:
        query = query.filter(AffectedZone.id.in_(request.zone_ids))
    zones = query.all()

    if not zones:
        raise HTTPException(status_code=404, detail="No zones found for this incident")

    predictions = []
    for zone in zones:
        for resource_type in ResourceTypeEnum:
            predicted_qty = calculate_baseline_demand(zone, resource_type, request.vulnerability_adjustment)

            prediction = DemandPrediction(
                zone_id=zone.id,
                resource_type=resource_type,
                predicted_quantity=predicted_qty,
                lower_bound=int(predicted_qty * 0.8),
                upper_bound=int(predicted_qty * 1.2),
                confidence_level=0.7,
                method="baseline_regression_v1",
                model_version="1.0",
                input_factors=f"population={zone.affected_population}, severity={zone.severity.value}, children={zone.vulnerable_children}, elderly={zone.vulnerable_elderly}, medical={zone.vulnerable_medical}",
                vulnerability_adjustment=request.vulnerability_adjustment
            )
            db.add(prediction)
            predictions.append(prediction)

    db.commit()
    for p in predictions:
        db.refresh(p)

    return predictions


@router.get("", response_model=List[DemandPredictionResponse])
async def list_predictions(
    zone_id: Optional[UUID] = None,
    resource_type: Optional[ResourceTypeEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DemandPrediction)

    if zone_id:
        query = query.filter(DemandPrediction.zone_id == zone_id)
    if resource_type:
        query = query.filter(DemandPrediction.resource_type == resource_type)

    predictions = query.order_by(desc(DemandPrediction.prediction_timestamp)).all()
    return predictions


@router.get("/{prediction_id}", response_model=DemandPredictionResponse)
async def get_prediction(prediction_id: UUID, db: Session = Depends(get_db)):
    prediction = db.query(DemandPrediction).filter(DemandPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


def calculate_baseline_demand(zone: AffectedZone, resource_type: ResourceTypeEnum, vulnerability_adjustment: float) -> int:
    pop = max(zone.affected_population, 1)
    severity_multiplier = {
        "critical": 1.5,
        "high": 1.2,
        "medium": 1.0,
        "low": 0.8
    }.get(zone.severity.value, 1.0)

    vulnerability_factor = 1.0 + (zone.vulnerable_children + zone.vulnerable_elderly + zone.vulnerable_medical) / max(pop, 1) * 0.3

    base_rates = {
        ResourceTypeEnum.food_packets: 2.0,
        ResourceTypeEnum.water: 3.0,
        ResourceTypeEnum.medical_kits: 0.1,
        ResourceTypeEnum.shelter: 0.3,
        ResourceTypeEnum.rescue_vehicles: 0.01,
        ResourceTypeEnum.personnel: 0.05,
        ResourceTypeEnum.fuel: 5.0,
        ResourceTypeEnum.generators: 0.005,
        ResourceTypeEnum.communication: 0.02,
        ResourceTypeEnum.other: 0.1
    }

    base_rate = base_rates.get(resource_type, 0.1)
    predicted = int(pop * base_rate * severity_multiplier * vulnerability_factor * vulnerability_adjustment)
    return max(predicted, 0)