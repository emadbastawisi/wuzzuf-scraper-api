from fastapi import Depends, Response , status , HTTPException , APIRouter
from sqlalchemy.orm import Session
from .. import models , schemas , Oauth2 ,database


router = APIRouter(
    prefix='/votes',
    tags=['Votes'],
)

@router.post('/' , status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db),current_user: int = Depends(Oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Post not found')
    vote_query=db.query(models.Vote).filter(models.Vote.post_id == vote.post_id , models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if(vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail=f'You already voted on this post')    
        new_vote = models.Vote(post_id=vote.post_id , user_id=current_user.id )
        db.add(new_vote)
        db.commit()
        return Response(status_code=status.HTTP_201_CREATED)
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail=f'You did not vote on this post')    
        vote_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)