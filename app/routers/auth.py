from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, database, utils, Oauth2
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication"])


@router.post('/login', response_model=schemas.LoginOut)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    if not utils.verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentialsd')
    access_token = Oauth2.create_access_token(data={"sub": str(user.id)})
    return {"username": user.username, "access_token": access_token, "token_type": "bearer"}
