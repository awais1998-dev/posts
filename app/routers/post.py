from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts'],
    dependencies=[Depends(oauth2.get_current_user)]
)

@router.get('/', response_model=List[schemas.PostOut])
def posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # posts = (db.query(models.Post).filter(models.Post.title.contains(search))
    #          .limit(limit)
    #          .offset(skip)
    #          .all())
    posts = ((db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
             .group_by(models.Post.id)).filter(models.Post.title.contains(search)).
             limit(limit).
             offset(skip).all())
    return posts

@router.post('/',response_model=schemas.PostResponse)
def create_post(post: schemas.Post, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get('/{id}', response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = (db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id).
            group_by(models.Post.id)).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Record Not Found')
    return post

@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.Post, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    query = db.query(models.Post).filter(models.Post.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Record Not Found')
    if query.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform this action')
    query.update(updated_post.dict())
    db.commit()
    return query.first()

@router.delete('/{id}')
def delete_post(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Record Not Found')
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform this action')
    db.delete(post)
    db.commit()
    return 'Record Deleted'

# @router.delete('/')
# def delete_posts(ids: List[int], db: Session = Depends(get_db)):
#     deleted_count = db.query(models.Post).filter(models.Post.id.in_(ids)).delete(synchronize_session=False)
#     db.commit()
#     if deleted_count == 0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No Records Found')
#     return f'{deleted_count} Record(s) Deleted'