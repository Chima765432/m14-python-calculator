from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationCreate, CalculationRead
from app.auth import create_access_token
from app.dependencies import get_current_user
from app.schemas.user import UserCreate, UserLogin, UserRead, UserToken

app = FastAPI(title="Calculations API")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.post("/users/register", response_model=UserToken, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=User.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.email)
    return UserToken(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        access_token=token,
    )


@app.post("/users/login", response_model=UserToken)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not user.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.email)
    return UserToken(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        access_token=token,
    )


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return (
        db.query(Calculation)
        .filter(Calculation.user_id == user.id)
        .order_by(Calculation.id)
        .all()
    )


@app.get("/calculations/{calculation_id}", response_model=CalculationRead)
def read_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = db.get(Calculation, calculation_id)
    if calculation is None or calculation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@app.post("/calculations", response_model=CalculationRead, status_code=201)
def add_calculation(
    payload: CalculationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = Calculation(
        a=payload.a, b=payload.b, type=payload.type.value, user_id=user.id
    )
    calculation.compute()
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


@app.put("/calculations/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int,
    payload: CalculationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = db.get(Calculation, calculation_id)
    if calculation is None or calculation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Calculation not found")
    calculation.a = payload.a
    calculation.b = payload.b
    calculation.type = payload.type.value
    calculation.compute()
    db.commit()
    db.refresh(calculation)
    return calculation


@app.delete("/calculations/{calculation_id}", status_code=204)
def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = db.get(Calculation, calculation_id)
    if calculation is None or calculation.user_id != user.id:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calculation)
    db.commit()
