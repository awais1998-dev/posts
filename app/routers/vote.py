from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, database, oauth2

router = APIRouter(
    prefix="/votes",
    tags=["Vote"]
)

@router.post("/")
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    voteExist = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                             models.Vote.user_id == current_user.id).first()
    if not voteExist:
        new_vote = models.Vote(user_id= current_user.id, post_id= vote.post_id)
        db.add(new_vote)
        db.commit()
        return {'Post Liked'}
    else:
        db.delete(voteExist)
        db.commit()
        return {'Post Disliked'}