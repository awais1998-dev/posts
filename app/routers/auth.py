from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, schemas, models, oauth2
from werkzeug.security import check_password_hash
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')

    if not check_password_hash(user.password, credentials.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')

    access_token = oauth2.create_access_token({'username': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}