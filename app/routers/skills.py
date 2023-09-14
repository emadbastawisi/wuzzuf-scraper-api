
from fastapi import Depends,  status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, schemas, Oauth2
from ..database import get_db

router = APIRouter(
    prefix='/skills',
    tags=['Skills'],
    responses={404: {"description": "Not found"}}
)

# add skills


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_skills(
    request: list[schemas.skill],
    db: Session = Depends(get_db),
):
    try:
        for skill in request:
            new_skill = models.Skills(
                name=skill.name,
                frequency=skill.frequency
            )
            db.add(new_skill)
            db.commit()
            db.refresh(new_skill)
        # Return the newly created keywords
        return status.HTTP_201_CREATED
    except SQLAlchemyError as e:
        # If there is a SQLAlchemy error, raise an HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# get top 10 matching skills with heightes frequency


@router.get('/{request}', response_model=list[schemas.skill])
def get_skills(
    request: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        skills = db.query(models.Skills).filter(models.Skills.name.ilike(
            f'{request}%')).order_by(models.Skills.frequency.desc()).limit(10).all()
        return skills
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
