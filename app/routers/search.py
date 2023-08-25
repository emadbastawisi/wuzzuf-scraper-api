from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, schemas, Oauth2, utils
from ..database import get_db

router = APIRouter(
    prefix='/search',
    tags=['Search'],
    # responses={404: {"description": "Not found"}}
)


# get user search_keywords
@router.get('/', response_model=schemas.Out_Search_Keyword)
def get_search_keywords(
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    # Try to get the User_Keyword object from the database
    try:
        user_query = db.query(models.User_Keyword).filter(
            models.User_Keyword.user_id == current_user.id
        ).first()

        # If the User_Keyword object exists, return the keywords
        if user_query:
            return user_query
        # If the User_Keyword object does not exist, raise an HTTPException
        else:
            raise HTTPException(
                status_code=404, detail="User has no search keywords"
            )

    # If there is an error during the database query, raise an HTTPException
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# add search_keywords
@router.post('/', status_code=status.HTTP_201_CREATED)
def add_search_keyword(
    request: schemas.keywords,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        # Check if there is an existing keyword entry for the current user
        user_query = db.query(models.User_Keyword).filter(
            models.User_Keyword.user_id == current_user.id
        ).first()

        if user_query:
            # If the keyword already exists, raise an error
            if request.keywords in user_query.keywords.split(','):
                raise HTTPException(
                    status_code=400, detail="keyword already exists"
                )
            else:
                # If the keyword does not exist, add it to the existing keywords
                new_keywords = user_query.keywords + ',' + request.keywords
                db.query(models.User_Keyword).filter(
                    models.User_Keyword.user_id == current_user.id
                ).update({models.User_Keyword.keywords: new_keywords})
                db.commit()
                db.refresh(user_query)

            # Return the updated keywords
            return user_query.keywords
        else:
            # If there is no existing keyword entry, create a new one
            new_user_keywords = models.User_Keyword(
                user_id=current_user.id, keywords=request.keywords
            )
            db.add(new_user_keywords)
            db.commit()
            db.refresh(new_user_keywords)

            # Return the newly created keywords
            return new_user_keywords.keywords
    except SQLAlchemyError as e:
        # If there is a SQLAlchemy error, raise an HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# delete search_keywords


@router.patch('/', status_code=status.HTTP_200_OK)
def delete_search_keyword(
    request: schemas.keywords,  # Request body containing the keywords to be deleted
    db: Session = Depends(get_db),  # Database session dependency
    current_user: int = Depends(
        Oauth2.get_current_user)  # Current logged-in user
):
    try:
        # Retrieve the user's keyword entry from the database
        user_query = db.query(models.User_Keyword).filter(
            models.User_Keyword.user_id == current_user.id).first()

        # Check if the user has any keywords
        if user_query:
            # Split the list of keywords received from the request
            list_of_keywords = request.keywords.split(',')
            # Split the user's existing keywords
            user_keywords = user_query.keywords.split(',')

            # Check if the keywords to be deleted are present in the user's existing keywords
            if list(set(list_of_keywords).intersection(user_keywords)) == []:
                # If no matching keywords found, raise an HTTPException with a 404 status code
                raise HTTPException(
                    status_code=404, detail="user doesn't have these keywords"
                )

            # Iterate through the keywords to be deleted
            for keyword in list_of_keywords:
                if keyword in user_keywords:
                    # Remove the keyword from the user's existing keywords
                    new_keywords = utils.remove_word(
                        keyword, user_query.keywords)

                    # If all keywords have been removed, delete the user's keyword entry
                    if new_keywords == '':
                        db.query(models.User_Keyword).filter(
                            models.User_Keyword.user_id == current_user.id
                        ).delete(synchronize_session=False)
                        db.commit()
                        # Return a response with a 204 status code (No Content)
                        return Response(status_code=status.HTTP_204_NO_CONTENT)
                    else:
                        # Update the user's keyword entry with the new keywords
                        db.query(models.User_Keyword).filter(
                            models.User_Keyword.user_id == current_user.id
                        ).update({models.User_Keyword.keywords: new_keywords})
                        db.commit()
                        # Refresh the user's keyword entry in the database
                        db.refresh(user_query)

            # Return the updated user's keywords
            return user_query.keywords
        else:
            # If the user has no keywords, raise an HTTPException with a 404 status code
            raise HTTPException(
                status_code=404, detail="user has no search keywords"
            )
    except SQLAlchemyError as e:
        # If any SQLAlchemyError occurs, raise an HTTPException with a 500 status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
