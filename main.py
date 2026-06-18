from fastapi import FastAPI

from routes.query_routes import router as query_router
from routes.anomaly_routes import router as anomaly_router
from routes.health_routes import router as health_router

app = FastAPI(
    title="Support Ticket AI"
)

app.include_router(query_router)
app.include_router(anomaly_router)
app.include_router(health_router)