from typing import Optional
from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .get_jobs_from_wuzzuf import get_jobs_from_wuzzuf_toDb
from .. import models, schemas, Oauth2
from ..database import get_db

router = APIRouter(
    prefix='/jobs',
    tags=['Jobs'],
    responses={404: {"description": "Not found"}}
)


# all new jobs to the database every 24 hours
@router.get('/', status_code=status.HTTP_201_CREATED)
def scrap_jobs(db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    try:
        # Call the function get_jobs_from_wuzzuf_toDb with the provided URL.
        get_jobs_from_wuzzuf_toDb(
            'https://wuzzuf.net/search/jobs/?filters%5Bpost_date%5D%5B0%5D=within_24_hours&start=0', db)

        # Return the HTTP status code 201 Created indicating that the request was successful.
        return status.HTTP_201_CREATED

    except Exception as e:
        # Return the HTTP status code 500 Internal Server Error indicating that an unexpected error occurred.
        return status.HTTP_500_INTERNAL_SERVER_ERROR


# search jobs based on user list of selected search keywords
@router.get('/{request}', response_model=list[schemas.JobOut])
def get_jobs(request: str, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    # Split the search keywords by commas into a list
    list_of_keywords = request.split(',')
    # Perform a database query to find jobs that have any of the keywords in their skills or title
    keyword_results = db.query(models.Job).filter(or_(*[models.Job.skills.ilike(f'%{keyword}%') for keyword in list_of_keywords], *[
        models.Job.title.ilike(f'%{keyword}%') for keyword in list_of_keywords]))
    keyword_results = keyword_results.all()

    # Return the keyword results
    return keyword_results
