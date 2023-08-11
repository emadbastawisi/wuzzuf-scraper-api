from fastapi import Depends, Response , status , HTTPException , APIRouter
from sqlalchemy.orm import Session
from .. import models , schemas , utils
from ..database import engine, get_db 

router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={404: {"description": "Not found"}}

)

# get all users
@router.get('/' , response_model=list[schemas.User])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# create a new user
@router.post('/', status_code=status.HTTP_201_CREATED , response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get a single user
@router.get('/{user_id}', response_model=schemas.UserOut)
def get_user(user_id: int , db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# delete a user
@router.delete('/{user_id}' ,status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int , db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == user_id)
    if user_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
