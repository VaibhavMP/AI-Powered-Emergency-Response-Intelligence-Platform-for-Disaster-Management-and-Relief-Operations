import requests
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.database.models import Incident, DataSourceRecord, DisasterTypeEnum, IncidentStatusEnum, SeverityEnum
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)

GDACS_URL = "https://www.gdacs.org/xml/rss.xml"


async def ingest_gdacs(db: Session) -> int:
    try:
        response = requests.get(GDACS_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch GDACS feed: {e}")
        record = DataSourceRecord(
            source_name="gdacs",
            source_type="rss_feed",
            raw_data=str(e)[:1000],
            processed=False,
            processing_status="error",
            error_message=str(e)
        )
        db.add(record)
        db.commit()
        return 0

    record = DataSourceRecord(
        source_name="gdacs",
        source_type="rss_feed",
        raw_data=response.text[:5000],
        processed=True,
        processing_status="processing"
    )
    db.add(record)
    db.commit()

    try:
        root = ET.fromstring(response.content)
        ns = {'': 'http://purl.org/rss/1.0/'}

        count = 0
        for item in root.findall('.//item'):
            try:
                title = item.find('title').text if item.find('title') is not None else ""
                description = item.find('description').text if item.find('description') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                guid = item.find('guid').text if item.find('guid') is not None else link

                existing = db.query(DataSourceRecord).filter(
                    DataSourceRecord.source_name == "gdacs",
                    DataSourceRecord.external_id == guid
                ).first()
                if existing:
                    continue

                disaster_type = classify_disaster_type(title + " " + description)
                severity = classify_severity(description)
                lat, lon = extract_coordinates(description)

                if lat is None or lon is None:
                    continue

                incident = Incident(
                    name=title[:255],
                    disaster_type=disaster_type,
                    severity=severity,
                    description=description[:2000],
                    longitude=lon,
                    latitude=lat,
                    status=IncidentStatusEnum.active,
                    reported_by="GDACS",
                    source_id="gdacs",
                    external_id=guid
                )
                db.add(incident)
                count += 1

            except Exception as e:
                logger.warning(f"Failed to parse GDACS item: {e}")
                continue

        record.processed = True
        record.processing_status = "completed"
        record.processed_at = datetime.utcnow()
        db.commit()
        logger.info(f"GDACS ingestion completed: {count} new incidents")
        return count

    except Exception as e:
        logger.error(f"GDACS processing failed: {e}")
        record.processed = False
        record.processing_status = "error"
        record.error_message = str(e)
        db.commit()
        return 0


async def ingest_usgs_earthquake(db: Session) -> int:
    USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

    try:
        response = requests.get(USGS_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"Failed to fetch USGS feed: {e}")
        record = DataSourceRecord(
            source_name="usgs_earthquake",
            source_type="geojson_feed",
            raw_data=str(e)[:1000],
            processed=False,
            processing_status="error",
            error_message=str(e)
        )
        db.add(record)
        db.commit()
        return 0

    record = DataSourceRecord(
        source_name="usgs_earthquake",
        source_type="geojson_feed",
        raw_data=response.text[:5000],
        processed=True,
        processing_status="processing"
    )
    db.add(record)
    db.commit()

    try:
        count = 0
        for feature in data.get('features', []):
            try:
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                coords = geom.get('coordinates', [])

                if len(coords) < 2:
                    continue

                lon, lat = coords[0], coords[1]
                mag = props.get('mag', 0)
                place = props.get('place', 'Unknown location')
                quake_id = feature.get('id', '')
                time_ms = props.get('time', 0)
                quake_time = datetime.fromtimestamp(time_ms / 1000) if time_ms else datetime.utcnow()

                external_id = f"usgs_{quake_id}"

                existing = db.query(DataSourceRecord).filter(
                    DataSourceRecord.source_name == "usgs_earthquake",
                    DataSourceRecord.external_id == external_id
                ).first()
                if existing:
                    continue

                disaster_type = DisasterTypeEnum.earthquake
                severity = classify_severity_by_magnitude(mag)

                incident = Incident(
                    name=f"Earthquake: {place}"[:255],
                    disaster_type=disaster_type,
                    severity=severity,
                    description=f"Magnitude {mag} earthquake at {place}. Time: {quake_time.isoformat()}",
                    longitude=lon,
                    latitude=lat,
                    status=IncidentStatusEnum.active,
                    reported_by="USGS",
                    source_id="usgs_earthquake",
                    external_id=external_id,
                    start_date=quake_time
                )
                db.add(incident)
                count += 1

            except Exception as e:
                logger.warning(f"Failed to parse USGS feature: {e}")
                continue

        record.processed = True
        record.processing_status = "completed"
        record.processed_at = datetime.utcnow()
        db.commit()
        logger.info(f"USGS ingestion completed: {count} new incidents")
        return count

    except Exception as e:
        logger.error(f"USGS processing failed: {e}")
        record.processed = False
        record.processing_status = "error"
        record.error_message = str(e)
        db.commit()
        return 0


def classify_disaster_type(text: str) -> DisasterTypeEnum:
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['flood', 'flooding', 'inundation']):
        return DisasterTypeEnum.flood
    elif any(kw in text_lower for kw in ['earthquake', 'quake', 'seismic', 'tremor']):
        return DisasterTypeEnum.earthquake
    elif any(kw in text_lower for kw in ['cyclone', 'hurricane', 'typhoon', 'tropical storm']):
        return DisasterTypeEnum.cyclone
    elif any(kw in text_lower for kw in ['wildfire', 'forest fire', 'bushfire', 'fire']):
        return DisasterTypeEnum.wildfire
    elif any(kw in text_lower for kw in ['drought', 'dry spell', 'water shortage']):
        return DisasterTypeEnum.drought
    elif any(kw in text_lower for kw in ['landslide', 'mudslide', 'rockfall']):
        return DisasterTypeEnum.landslide
    elif any(kw in text_lower for kw in ['tsunami', 'tidal wave']):
        return DisasterTypeEnum.tsunami
    elif any(kw in text_lower for kw in ['volcano', 'volcanic', 'eruption']):
        return DisasterTypeEnum.volcano
    return DisasterTypeEnum.other


def classify_severity(text: str) -> SeverityEnum:
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['catastrophic', 'extreme', 'devastating', 'major disaster']):
        return SeverityEnum.critical
    elif any(kw in text_lower for kw in ['severe', 'serious', 'significant', 'major']):
        return SeverityEnum.high
    elif any(kw in text_lower for kw in ['moderate', 'considerable']):
        return SeverityEnum.medium
    elif any(kw in text_lower for kw in ['minor', 'small', 'localized']):
        return SeverityEnum.low
    return SeverityEnum.medium


def classify_severity_by_magnitude(mag: float) -> SeverityEnum:
    if mag >= 7.0:
        return SeverityEnum.critical
    elif mag >= 6.0:
        return SeverityEnum.high
    elif mag >= 5.0:
        return SeverityEnum.medium
    elif mag >= 4.0:
        return SeverityEnum.low
    return SeverityEnum.low


def extract_coordinates(text: str):
    import re
    patterns = [
        r'(\-?\d+\.?\d*)\s*[°,]\s*(\-?\d+\.?\d*)',
        r'lat[:\s]*(\-?\d+\.?\d*)\s*[,\s]*lon[:\s]*(\-?\d+\.?\d*)',
        r'latitude[:\s]*(\-?\d+\.?\d*)\s*[,\s]*longitude[:\s]*(\-?\d+\.?\d*)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                lat, lon = float(matches[0][0]), float(matches[0][1])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
            except (ValueError, IndexError):
                continue
    return None, None