from datetime import datetime, timedelta
from app.models.refresh_token import RefreshToken
from app.core.security import REFRESH_TOKEN_EXPIRE_DAYS

def save_refresh_token(db, user_id: str, token: str):
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(rt)
    db.commit()

def revoke_refresh_token(db, token: str):
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    db.commit()
