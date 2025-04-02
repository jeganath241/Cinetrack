from fastapi import APIRouter
from app.api.v1.endpoints import auth, content, watchlist, bucketlist, recommendations, custom_lists, goals, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(bucketlist.router, prefix="/bucketlist", tags=["bucketlist"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(custom_lists.router, prefix="/lists", tags=["custom_lists"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 