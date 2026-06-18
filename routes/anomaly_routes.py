from fastapi import APIRouter

from anomaly_services import detect_anomalies

router = APIRouter(
    tags=["Anomalies"]
)

@router.get("/anomalies")
def anomalies():

    return detect_anomalies()