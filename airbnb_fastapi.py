import json
from datetime import date, datetime, timedelta

from airbnb_api import Airbnb
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "views": 3,
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    views: int
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Airbnb",
    description="Airbnb service scrapy info from Items",
    version="0.1",
    # terms_of_service="http://example.com/terms/",
    contact={"telegram": "https://t.me/pydevdse", }

    # {
    #     "name": "Michael",
    #     #"url": "http://x-force.example.com/contact/",
    #     "telegram": "https://t.me/pydevdse",
    #     #"email": "dp@x-force.example.com",
    # },
    #license_info={
    #    "name": "Apache 2.0",
    #    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    #},
)



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    print(current_user)
    return [{"owner": current_user.username, "requests": fake_users_db.get(current_user.username).get("views")}]


@app.get("/item_info/{item_id}")
async def read_item_info(
    item_id: int, current_user: Annotated[User, Depends(get_current_active_user)]
):
    response = Airbnb().get_room_info(item_id)
    if response is not None:
        if fake_users_db.get(current_user.username).get("views")<1:
            raise HTTPException(status_code=400, detail="Requests not")
        fake_users_db[current_user.username]["views"] -= 1
    print(current_user)
    return response


@app.get("/item_info_price/{item_id}")
async def read_item_price(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    checkIn: date = datetime.now().date(),
    checkOut: date = date(
        year=datetime.now().date().year,
        month=datetime.now().date().month,
        day=datetime.now().date().day + 4,
    ),
):
    return Airbnb().get_room_info_price(item_id, checkIn, checkOut)


@app.get("/item_info_available/{item_id}")
async def read_item_available(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    month: int = datetime.now().month,
):
    return Airbnb().get_room_available(item_id, month)
