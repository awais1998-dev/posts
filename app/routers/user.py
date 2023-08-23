from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from werkzeug.security import generate_password_hash

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post('/', response_model=schemas.UserResponse)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    user.password = generate_password_hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}', response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Record not found')
    return user