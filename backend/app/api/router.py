from fastapi import APIRouter

from app.api.routes import incidents, zones, resources, depots, personnel, predictions, allocations, missions, dashboard, data_sources, analytics, reports

api_router = APIRouter()

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(zones.router, prefix="/zones", tags=["Affected Zones"])
api_router.include_router(depots.router, prefix="/depots", tags=["Resource Depots"])
api_router.include_router(resources.router, prefix="/resources", tags=["Resources & Inventory"])
api_router.include_router(personnel.router, prefix="/personnel", tags=["Personnel"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Demand Predictions"])
api_router.include_router(allocations.router, prefix="/allocations", tags=["Resource Allocations"])
api_router.include_router(missions.router, prefix="/missions", tags=["Missions"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["Data Sources"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])