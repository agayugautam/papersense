from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def placeholder():
    return {"message": "Search API alive"}
