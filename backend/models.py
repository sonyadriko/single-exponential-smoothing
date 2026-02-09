from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # 'admin' or 'owner'
    
    forecasts = relationship("Forecast", back_populates="created_by_user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, nullable=True)

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    product_name = Column(String, index=True)
    qty = Column(Integer)

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=True, index=True)
    created_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    alpha = Column(Float)
    product_name = Column(String)
    next_period_forecast = Column(Float)
    mape = Column(Float)
    calculation_steps = Column(JSON)
    
    created_by_user = relationship("User", back_populates="forecasts")
