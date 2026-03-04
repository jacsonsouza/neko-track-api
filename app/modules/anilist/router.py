from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dep import AuthClaims, claims
from app.db.session import get_db
from app.modules.anilist.service import viewer

router = APIRouter(prefix="/anilist", tags=["anilist"])


@router.get("/viewer")
async def get_viewer(
    claims: AuthClaims = Depends(claims), db: Session = Depends(get_db)
):
    return await viewer(db, user_id=claims.user_id)
