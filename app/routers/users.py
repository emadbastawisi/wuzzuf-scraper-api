from datetime import datetime
import io
import pickle
from fastapi import Depends, File, Response, UploadFile, status, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, schemas, utils, Oauth2
from ..database import engine, get_db


router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={404: {"description": "Not found"}}

)

# get all users


@router.get('/', response_model=list[schemas.UserProfile])
async def get_users(db: Session = Depends(get_db)):
    # Retrieve all users from the database
    users = db.execute(select(models.User)).scalars().all()
    # Return the list of users as the API response
    return users

# create a new user


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreateOut)
def create_user(user: schemas.UserCreateIn, db: Session = Depends(get_db)):
    if user.email == '' or user.first_name == '' or user.last_name == '' or user.password == '':
        raise HTTPException(status_code=400, detail="Invalid data")
    existing_user = db.query(models.User).filter(
        models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    hashed_password = utils.hash(user.password)

    new_user = models.User(
        user.model_dump()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# get current user


@router.get('/current', response_model=schemas.CurrentUserOut)
def get_current_user(db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(
            models.User.id == current_user.id).first()
        if not user:
            return False
        return user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# get user profile


@router.get('/profile', response_model=schemas.UserProfile)
def get_current_user(db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    try:
        user = db.query(models.User).filter(
            models.User.id == current_user.id).first()
        if not user:
            return False
        return user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# update user password

@router.patch('/password', status_code=status.HTTP_200_OK)
def update_password(password: schemas.Password, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authorized")
    user.password = utils.hash(password.password)
    db.commit()
    return Response(status_code=status.HTTP_200_OK)

# delete user by id


@router.delete('/deleteUser/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# get user by id


@router.get('/email/{email}')
def get_user(email: str, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(
            models.User.email == email).first()
        if not user:
            return True
        return False
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# add user career interests


@router.post('/addCareerInterests', status_code=status.HTTP_201_CREATED, response_model=schemas.UserProfile)
def add_career_interests(
    request: schemas.UserCareerInterests,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        # Check if there is an existing career interests entry for the current user
        user_query = db.query(models.User_Career_Interests).filter(
            models.User_Career_Interests.user_id == current_user.id
        ).first()

        if user_query:
            db.query(models.User_Career_Interests).filter(
                models.User_Career_Interests.user_id == current_user.id
            ).update(
                request.model_dump(), synchronize_session=False)
        else:
            # If there is no existing career interests entry, create a new one
            new_user_career_interests = models.User_Career_Interests(
                **request.model_dump(),
                user_id=current_user.id
            )
            db.add(new_user_career_interests)

        db.commit()
        # Return the updated user profile
        return current_user
    except SQLAlchemyError as e:
        # If there is a SQLAlchemy error, raise an HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# add user career interests


@router.post('/addPersonalInfo', status_code=status.HTTP_201_CREATED, response_model=schemas.UserProfile)
def add_personal_info(
    request: schemas.UserPersonalInfoIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        request_dict = vars(request)
        personal_info = {key: value for key, value in request_dict.items() if key not in [
            'first_name', 'last_name']}
        db.query(models.User).filter(
            models.User.id == current_user.id
        ).update({
            'first_name': request.first_name,
            'last_name': request.last_name
        }, synchronize_session=False)

        user_query = db.query(models.User_Personal_Info).filter(
            models.User_Personal_Info.user_id == current_user.id
        ).first()
        if user_query:
            db.query(models.User_Personal_Info).filter(
                models.User_Personal_Info.user_id == current_user.id
            ).update(personal_info, synchronize_session=False)
        else:
            new_User_Personal_Info = models.User_Personal_Info(
                **personal_info,
                user_id=current_user.id
            )
            db.add(new_User_Personal_Info)
        db.commit()
        return current_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# get user cv


@router.get('/cv',)
def get_cv(
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        user_query = db.query(models.User_Cv).filter(
            models.User_Cv.user_id == current_user.id
        ).first()
        if not user_query:
            raise HTTPException(status_code=404, detail="CV not found")

        # Create a StreamingResponse to send the file to the client
        response = StreamingResponse(io.BytesIO(
            user_query.cv_file), media_type="application/pdf")
        response.headers["Content-Disposition"] = f"attachment; filename={user_query.cv_name}"
        return response
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# add user cv


@router.post('/addCV', status_code=status.HTTP_201_CREATED, response_model=schemas.UserProfile)
async def add_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        contents = await file.read()
        # check if user already has a cv entery
        user_query = db.query(models.User_Cv).filter(
            models.User_Cv.user_id == current_user.id
        ).first()
        if user_query:
            db.query(models.User_Cv).filter(
                models.User_Cv.user_id == current_user.id
            ).update({
                'cv_file': contents,
                'cv_name': file.filename,
                'updated_at': datetime.now()
            }, synchronize_session=False)
        else:
            new_user_cv = models.User_Cv(
                cv_file=contents,
                cv_name=file.filename,
                user_id=current_user.id
            )
            db.add(new_user_cv)
        db.commit()
        return current_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# delete user cv

@router.delete('/deleteCV', response_model=schemas.UserProfile)
def delete_cv(
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        user_query = db.query(models.User_Cv).filter(
            models.User_Cv.user_id == current_user.id
        ).first()

        if not user_query:
            raise HTTPException(status_code=404, detail="CV not found")

        db.query(models.User_Cv).filter(
            models.User_Cv.user_id == current_user.id
        ).delete(synchronize_session=False)
        db.commit()
        return current_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# add work experience


@router.post('/addWorkExperience', status_code=status.HTTP_201_CREATED, response_model=schemas.UserProfile)
def add_work_experience(
    request: schemas.UserWorkExperience,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        new_user_work_experience = models.User_Work_Experience(
            **request.model_dump(),
            user_id=current_user.id
        )
        db.add(new_user_work_experience)

        db.commit()
        return current_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

# update work experience


@router.patch('/updateWorkExperience', status_code=status.HTTP_200_OK)
def update_work_experience(
    request: schemas.UserWorkExperienceOut,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        user_query = db.query(models.User_Work_Experience).filter(
            models.User_Work_Experience.user_id == current_user.id &
            models.User_Work_Experience.id == request.id
        ).first()

        if not user_query:
            raise HTTPException(
                status_code=404, detail="Work Experience not found")

        db.query(models.User_Work_Experience).filter(
            models.User_Work_Experience.user_id == current_user.id
        ).update({**request.model_dump(), 'updated_at': datetime.now()}, synchronize_session=False)
        db.commit()
        return current_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# delete work experience


@router.delete('/deleteWorkExperience', response_model=schemas.UserProfile)
def delete_work_experience(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(Oauth2.get_current_user)
):
    try:
        user_query = db.query(models.User_Work_Experience).filter(
            models.User_Work_Experience.user_id == current_user.id &
            models.User_Work_Experience.id == id
        ).first()

        if not user_query:
            raise HTTPException(
                status_code=404, detail="Work Experience not found")

        db.query(models.User_Work_Experience).filter(
            models.User_Work_Experience.user_id == current_user.id
        ).delete(synchronize_session=False)
        db.commit()
        return current_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
