from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import models, database
from database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Depot Jawara SES Forecasting")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security Config ---
SECRET_KEY = "supersecretkey" # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class ProductCreate(BaseModel):
    name: str

class ProductOut(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class SaleCreate(BaseModel):
    date: str
    product_name: str
    qty: int

class SaleOut(SaleCreate):
    id: int
    class Config:
        orm_mode = True

class ForecastRequest(BaseModel):
    alpha: float
    product_name: Optional[str] = None
    project_name: Optional[str] = None
    next_period_date: Optional[str] = None

# --- Auth Helpers ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# --- Endpoints ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

# --- Initialization ---
@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    # Check if admin exists
    if not db.query(models.User).filter(models.User.username == "admin").first():
        admin = models.User(username="admin", hashed_password=get_password_hash("admin123"), role="admin")
        db.add(admin)
    # Check if owner exists
    if not db.query(models.User).filter(models.User.username == "owner").first():
        owner = models.User(username="owner", hashed_password=get_password_hash("owner123"), role="owner")
        db.add(owner)
    
    # Check if products exist, if not seed them
    if db.query(models.Product).count() == 0:
        seed_products(db)
    
    # Check if data exists, if not seed May data
    if db.query(models.Sale).count() == 0:
        seed_may_data(db)
        
    db.commit()
    db.close()

def seed_products(db: Session):
    PRODUCTS = ["Soto Ayam", "Nasi Goreng Jawa", "Nasi Bebek Biasa", "Nasi Ayam", "Nasi Lele", "Nasi 3T", "Es Teh", "Es Jeruk"]
    for product_name in PRODUCTS:
        if not db.query(models.Product).filter(models.Product.name == product_name).first():
            product = models.Product(name=product_name, created_at=datetime.utcnow())
            db.add(product)

def seed_may_data(db: Session):
    # May Data
    MAY_DATA_RAW = [
        ["01-May-25", 21, 9, 23, 14, 17, 19, 21, 12],
        ["02-May-25", 20, 4, 19, 17, 20, 20, 16, 20],
        ["03-May-25", 18, 12, 21, 20, 28, 19, 17, 23],
        ["04-May-25", 20, 8, 16, 24, 24, 24, 8, 16],
        ["05-May-25", 22, 6, 20, 14, 18, 21, 15, 8],
        ["06-May-25", 19, 7, 24, 12, 25, 15, 19, 10],
        ["07-May-25", 14, 6, 10, 13, 15, 12, 17, 11],
        ["08-May-25", 18, 3, 16, 15, 15, 18, 20, 7],
        ["09-May-25", 20, 5, 20, 14, 11, 24, 21, 9],
        ["10-May-25", 21, 15, 14, 20, 17, 19, 19, 16],
        ["11-May-25", 19, 6, 12, 16, 21, 14, 21, 15],
        ["12-May-25", 20, 11, 16, 9, 17, 17, 15, 10],
        ["13-May-25", 16, 18, 15, 12, 15, 19, 18, 9],
        ["14-May-25", 18, 9, 12, 11, 16, 16, 16, 14],
        ["15-May-25", 14, 9, 10, 13, 12, 13, 11, 10],
        ["16-May-25", 16, 16, 14, 17, 18, 15, 22, 18],
        ["17-May-25", 18, 10, 9, 10, 17, 11, 20, 13],
        ["18-May-25", 12, 8, 11, 8, 19, 17, 16, 15],
        ["19-May-25", 14, 11, 15, 11, 17, 12, 10, 11],
        ["20-May-25", 16, 15, 12, 13, 14, 11, 19, 10],
        ["21-May-25", 12, 13, 10, 14, 18, 8, 15, 12],
        ["22-May-25", 11, 8, 9, 9, 16, 11, 18, 11],
        ["23-May-25", 16, 9, 8, 10, 13, 14, 23, 10],
        ["24-May-25", 13, 4, 11, 11, 16, 10, 21, 9],
        ["25-May-25", 11, 5, 12, 14, 14, 9, 19, 11],
        ["26-May-25", 15, 7, 14, 9, 13, 8, 16, 7],
        ["27-May-25", 12, 3, 9, 7, 11, 16, 18, 9],
        ["28-May-25", 10, 12, 8, 12, 15, 20, 15, 6],
        ["29-May-25", 8, 7, 10, 6, 11, 10, 18, 10],
        ["30-May-25", 11, 6, 7, 9, 12, 12, 17, 15],
        ["31-May-25", 9, 9, 11, 10, 15, 16, 14, 11],
    ]
    PRODUCTS = ["Soto Ayam", "Nasi Goreng Jawa", "Nasi Bebek Biasa", "Nasi Ayam", "Nasi Lele", "Nasi 3T", "Es Teh", "Es Jeruk"]
    
    for row in MAY_DATA_RAW:
        date = row[0]
        for i, product in enumerate(PRODUCTS):
            qty = row[i+1]
            sale = models.Sale(date=date, product_name=product, qty=qty)
            db.add(sale)

# --- Sales Logic ---

def calculate_ses_with_steps(series: List[float], dates: List[str], alpha: float) -> Dict[str, Any]:
    if not series: 
        return {"forecasts": [], "steps": [], "mape": 0}
    
    forecasts = [series[0]]
    steps = []
    
    # Step 1: Initial forecast
    steps.append({
        "period": 1,
        "date": dates[0] if dates else "N/A",
        "actual": series[0],
        "forecast": series[0],
        "formula": "F₁ = A₁ (Initial)",
        "calculation": f"F₁ = {series[0]}",
        "result": series[0],
        "error": 0,
        "error_pct": 0
    })
    
    # Subsequent steps
    for i in range(1, len(series)):
        prev_actual = series[i-1]
        prev_forecast = forecasts[i-1]
        current_actual = series[i]
        
        # Calculate forecast
        next_forecast = alpha * prev_actual + (1 - alpha) * prev_forecast
        forecasts.append(next_forecast)
        
        # Calculate error
        error = abs(current_actual - next_forecast)
        error_pct = (error / current_actual * 100) if current_actual != 0 else 0
        
        steps.append({
            "period": i + 1,
            "date": dates[i] if dates and i < len(dates) else "N/A",
            "actual": current_actual,
            "forecast": next_forecast,
            "formula": f"F{i+1} = {alpha} × A{i} + (1-{alpha}) × F{i}",
            "calculation": f"F{i+1} = {alpha} × {prev_actual} + {1-alpha} × {prev_forecast}",
            "result": next_forecast,
            "error": error,
            "error_pct": error_pct
        })
    
    return {
        "forecasts": forecasts,
        "steps": steps,
        "mape": calculate_mape(series, forecasts)
    }

def calculate_mape(actual: List[float], forecast: List[float]) -> float:
    actual_np = np.array(actual)
    forecast_np = np.array(forecast)
    mask = actual_np != 0
    if not np.any(mask): return 0
    return np.mean(np.abs((actual_np[mask] - forecast_np[mask]) / actual_np[mask])) * 100

@app.post("/forecast")
async def create_forecast(request: ForecastRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_admin_user)):
    sales_query = db.query(models.Sale)
    if request.product_name:
        sales_query = sales_query.filter(models.Sale.product_name == request.product_name)
    
    sales = sales_query.all()
    if not sales:
        raise HTTPException(status_code=400, detail="No data available")

    data = [{"date": s.date, "product_name": s.product_name, "qty": s.qty} for s in sales]
    df = pd.DataFrame(data)

    results = {}
    total_mape = 0
    product_count = 0

    for product_name, group in df.groupby("product_name"):
        group = group.sort_values("date")
        dates = group["date"].tolist()
        actuals = group["qty"].tolist()
        
        calc_result = calculate_ses_with_steps(actuals, dates, request.alpha)
        forecasts = calc_result["forecasts"]
        steps = calc_result["steps"]
        mape = calc_result["mape"]
        
        next_forecast = request.alpha * actuals[-1] + (1 - request.alpha) * forecasts[-1]
        
        forecast_record = models.Forecast(
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            created_by=current_user.id,
            alpha=request.alpha,
            product_name=product_name,
            next_period_forecast=next_forecast,
            next_period_date=request.next_period_date,
            mape=mape,
            calculation_steps={
                "dates": dates,
                "actuals": actuals,
                "forecasts": forecasts,
                "steps": steps
            }
        )
        db.add(forecast_record)
        
        results[product_name] = {
            "dates": dates,
            "actuals": actuals,
            "forecasts": forecasts,
            "steps": steps,
            "mape": mape,
            "next_period_forecast": next_forecast,
            "next_period_date": request.next_period_date
        }
        total_mape += mape
        product_count += 1
    
    db.commit()
    
    return {
        "results": results,
        "overall_mape": total_mape / product_count if product_count > 0 else 0,
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/forecast/latest")
async def get_latest_forecast(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    latest = db.query(models.Forecast).order_by(models.Forecast.created_at.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="No forecast found")

    steps = latest.calculation_steps or {}
    return {
        "id": latest.id,
        "created_at": latest.created_at.isoformat(),
        "alpha": latest.alpha,
        "product_name": latest.product_name,
        "next_period_forecast": latest.next_period_forecast,
        "next_period_date": latest.next_period_date,
        "mape": latest.mape,
        "dates": steps.get("dates", []),
        "actuals": steps.get("actuals", []),
        "forecasts": steps.get("forecasts", []),
        "steps": steps.get("steps", [])
    }

@app.get("/forecasts/history")
async def get_forecast_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    forecasts = db.query(models.Forecast).order_by(models.Forecast.created_at.desc()).all()
    return [{
        "id": f.id,
        "created_at": f.created_at.isoformat(),
        "alpha": f.alpha,
        "product_name": f.product_name,
        "next_period_forecast": f.next_period_forecast,
        "next_period_date": f.next_period_date,
        "mape": f.mape
    } for f in forecasts]

@app.get("/sales", response_model=List[SaleOut])
async def get_sales(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Sale).order_by(models.Sale.date).all()

@app.post("/sales")
async def add_sale(sale: SaleCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    db_sale = models.Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    return {"status": "ok", "msg": "Sale added"}

@app.post("/reset-data")
async def reset_data(db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    db.query(models.Sale).delete()
    seed_may_data(db)
    db.commit()
    return {"status": "ok", "msg": "Data reset to initial May state"}

@app.get("/products", response_model=List[ProductOut])
async def get_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Product).all()

@app.post("/products")
async def create_product(product: ProductCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    existing = db.query(models.Product).filter(models.Product.name == product.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    
    db_product = models.Product(name=product.name, created_at=datetime.utcnow())
    db.add(db_product)
    db.commit()
    return {"status": "ok", "msg": "Product created"}

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if sales exist for this product
    sales_count = db.query(models.Sale).filter(models.Sale.product_name == product.name).count()
    if sales_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete product with {sales_count} sales records")
    
    db.delete(product)
    db.commit()
    return {"status": "ok", "msg": "Product deleted"}

@app.get("/sales", response_model=List[SaleOut])
async def get_sales(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Sale).order_by(models.Sale.date).all()

@app.get("/sales/product/{product_name}")
async def get_sales_by_product(product_name: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sales = db.query(models.Sale).filter(models.Sale.product_name == product_name).order_by(models.Sale.date).all()
    return [{"id": s.id, "date": s.date, "product_name": s.product_name, "qty": s.qty} for s in sales]

@app.post("/sales")
async def add_sale(sale: SaleCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    db_sale = models.Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    return {"status": "ok", "msg": "Sale added"}

@app.delete("/sales/{sale_id}")
async def delete_sale(sale_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    db.delete(sale)
    db.commit()
    return {"status": "ok", "msg": "Sale deleted"}

@app.post("/reset-data")
async def reset_data(db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    db.query(models.Sale).delete()
    db.query(models.Forecast).delete()
    seed_may_data(db)
    db.commit()
    return {"status": "ok", "msg": "Data reset to initial May state"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/forecast/projects")
async def get_forecast_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_admin_user)):
    from sqlalchemy import func
    
    projects = db.query(
        models.Forecast.project_name,
        func.min(models.Forecast.created_at).label('created_at'),
        func.min(models.User.username).label('created_by'),
        func.min(models.Forecast.alpha).label('alpha'),
        func.count(models.Forecast.id).label('forecast_count'),
        func.avg(models.Forecast.mape).label('overall_mape')
    ).join(
        models.User, models.User.id == models.Forecast.created_by
    ).filter(
        models.Forecast.project_name.isnot(None)
    ).group_by(
        models.Forecast.project_name
    ).all()
    
    return [{
        "project_name": p.project_name,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "created_by": p.created_by,
        "alpha": p.alpha,
        "forecast_count": p.forecast_count,
        "overall_mape": p.overall_mape
    } for p in projects]

@app.get("/forecast/project/{project_name}")
async def get_forecast_project(project_name: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    forecasts = db.query(models.Forecast).filter(
        models.Forecast.project_name == project_name
    ).all()
    
    if not forecasts:
        raise HTTPException(status_code=404, detail="Project not found")
    
    results = {}
    for f in forecasts:
        steps = f.calculation_steps or {}
        results[f.product_name] = {
            "dates": steps.get("dates", []),
            "actuals": steps.get("actuals", []),
            "forecasts": steps.get("forecasts", []),
            "steps": steps.get("steps", []),
            "mape": f.mape,
            "next_period_forecast": f.next_period_forecast,
            "next_period_date": f.next_period_date
        }
    
    overall_mape = sum(f.mape for f in forecasts) / len(forecasts) if forecasts else 0
    
    return {
        "project_name": project_name,
        "created_at": forecasts[0].created_at.isoformat(),
        "alpha": forecasts[0].alpha,
        "results": results,
        "overall_mape": overall_mape
    }

@app.put("/forecast/project/{project_name}")
async def update_forecast_project(project_name: str, new_name: str, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    forecasts = db.query(models.Forecast).filter(
        models.Forecast.project_name == project_name
    ).all()
    
    if not forecasts:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for f in forecasts:
        f.project_name = new_name
    
    db.commit()
    return {"status": "ok", "msg": "Project renamed"}

@app.delete("/forecast/project/{project_name}")
async def delete_forecast_project(project_name: str, db: Session = Depends(get_db), admin: models.User = Depends(get_admin_user)):
    forecasts = db.query(models.Forecast).filter(
        models.Forecast.project_name == project_name
    ).all()
    
    if not forecasts:
        raise HTTPException(status_code=404, detail="Project not found")
    
    count = len(forecasts)
    for f in forecasts:
        db.delete(f)
    
    db.commit()
    return {"status": "ok", "msg": f"Deleted {count} forecast(s)"}
