from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(20)) # 'admin' or 'owner'

    forecasts = relationship("Forecast", back_populates="created_by_user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, nullable=True)

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), index=True)
    product_name = Column(String(100), index=True)
    qty = Column(Integer)

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    alpha = Column(Float)
    product_name = Column(String(100))
    next_period_forecast = Column(Float)
    next_period_date = Column(String(20), nullable=True)
    mape = Column(Float)
    calculation_steps = Column(JSON)

    created_by_user = relationship("User", back_populates="forecasts")
