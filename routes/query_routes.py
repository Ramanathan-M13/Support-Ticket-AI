from fastapi import APIRouter

from models import QueryRequest
from query_engine_services import execute_query

router = APIRouter(
    tags=["Query"]
)

@router.post("/query")
def query(request: QueryRequest):

    return execute_query(
request.question
)
    