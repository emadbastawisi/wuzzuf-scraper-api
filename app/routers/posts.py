from typing import Optional
from fastapi import Depends, Response , status , HTTPException , APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models , schemas ,Oauth2
from ..database import get_db 

router = APIRouter(
    prefix='/posts',
    tags=['Posts'],
    responses={404: {"description": "Not found"}}
)

# get all posts
@router.get('/' , response_model=list[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user) ,limit: int = 10, skip: int = 0 ,search:Optional[str] = ''):
    
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    votes_query = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote , models.Post.id == models.Vote.post_id , isouter=True).group_by(models.Post.id)
    votes = votes_query.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return votes

# create a new post
@router.post('/', status_code=status.HTTP_201_CREATED , response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id ,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# get a single post
@router.get('/{post_id}' , response_model=schemas.PostOut)
def get_post(post_id: int , db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user)):
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote , models.Post.id == models.Vote.post_id , isouter=True).group_by(models.Post.id).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# delete a post
@router.delete('/{post_id}' ,status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int , db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update a post
@router.put('/{post_id}')
def update_post(post_id: int, post: schemas.PostCreate , db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user)):
    updated_post_query = db.query(models.Post).filter(models.Post.id == post_id)
    updated_post = updated_post_query.first()
    if updated_post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    updated_post_query.update(post.model_dump() , synchronize_session=False)
    db.commit()
    db.refresh(updated_post_query.first())
    return updated_post_query.first()