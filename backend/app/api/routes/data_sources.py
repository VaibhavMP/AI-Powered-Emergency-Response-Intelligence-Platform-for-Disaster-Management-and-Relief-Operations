from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database.connection import get_db
from app.database.models import DataSourceRecord, Incident
from app.database.schemas import DataSourceRecordResponse, DataSourceItem

router = APIRouter()


@router.get("", response_model=List[DataSourceItem])
async def list_data_sources(db: Session = Depends(get_db)):
    sources = [
        {
            "id": "gdacs",
            "name": "GDACS (Global Disaster Alert and Coordination System)",
            "type": "rss_feed",
            "url": "https://www.gdacs.org/xml/rss.xml",
            "description": "Global disaster alerts and impact estimates",
            "enabled": True,
            "last_sync": None,
            "status": "available"
        },
        {
            "id": "usgs_earthquake",
            "name": "USGS Earthquake Feed",
            "type": "geojson_feed",
            "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
            "description": "Real-time earthquake data from USGS",
            "enabled": True,
            "last_sync": None,
            "status": "available"
        },
        {
            "id": "ndma",
            "name": "NDMA (National Disaster Management Authority)",
            "type": "api",
            "url": "https://ndma.gov.in",
            "description": "Official Indian disaster management data (requires API access)",
            "enabled": False,
            "last_sync": None,
            "status": "not_configured"
        }
    ]
    return sources


@router.get("/records", response_model=List[DataSourceRecordResponse])
async def list_source_records(
    source_name: Optional[str] = None,
    processed: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(DataSourceRecord)

    if source_name:
        query = query.filter(DataSourceRecord.source_name == source_name)
    if processed is not None:
        query = query.filter(DataSourceRecord.processed == processed)

    records = query.order_by(desc(DataSourceRecord.retrieved_at)).limit(limit).all()
    return records


@router.post("/{source_name}/sync")
async def sync_data_source(source_name: str, db: Session = Depends(get_db)):
    if source_name not in ["gdacs", "usgs_earthquake"]:
        raise HTTPException(status_code=400, detail=f"Unknown or unsupported data source: {source_name}")

    from app.services.disaster_ingestion import ingest_gdacs, ingest_usgs_earthquake

    try:
        if source_name == "gdacs":
            count = await ingest_gdacs(db)
        else:
            count = await ingest_usgs_earthquake(db)

        return {"status": "success", "source": source_name, "records_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")