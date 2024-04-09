from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.concurrency import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import hashlib
from datetime import datetime, timedelta
import jwt

from models.db_models import User
from models.nn_model import Model as SummarizeModel
from models.user_model import User as ValidationUser, UserCreate, UserLogin, ActionBase, PredictionRequest

from credentials_local import creds


engine = create_engine(creds["db_url"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


PREDICTION_MODEL: SummarizeModel = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global PREDICTION_MODEL
    PREDICTION_MODEL = SummarizeModel()
    yield


app = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Security

def generate_token(user_id: int, expires_delta: timedelta):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + expires_delta
    }
    token = jwt.encode(payload, creds["secret_key"], algorithm="HS256")
    return token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, creds["secret_key"], algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_token(token)
    db_user = db.query(User).filter(User.id == user_id).first()
    return db_user


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# Routes

@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User.register(db, login=user.login, password=hashed_password)
    
    access_token = generate_token(db_user.id, timedelta(minutes=15))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User.authenticate(db, login=user.login, password=hashed_password)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = generate_token(db_user.id, timedelta(minutes=15))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/predict/")
def make_prediction(req: PredictionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if (len(req.input_text) > current_user.balance):
        raise HTTPException(400, "The user doesn't have enough coins")

    global PREDICTION_MODEL
    predict = PREDICTION_MODEL.make_prediction(req.input_text, req.min_len, req.max_len)[0]["summary_text"]
    current_user.make_action(db, req.input_text, predict)
    return predict


@app.get("/get_user/", response_model=ValidationUser)
def get_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/balance/increase")
def increase_balance(amount: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.increase_balance(db, amount)
    return {"message": "Balance increased successfully"}


@app.get("/history/", response_model=List[ActionBase])
def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user.get_history(db)
