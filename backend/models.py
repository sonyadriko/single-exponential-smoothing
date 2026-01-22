from sqlalchemy import Column, Integer, String, Date, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # 'admin' or 'owner'

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True) # Storing as string YYYY-MM-DD for simplicity in this prototype
    product_name = Column(String, index=True)
    qty = Column(Integer)
