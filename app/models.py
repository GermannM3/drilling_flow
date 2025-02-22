from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    telegram_id = Column(String, nullable=True)
    
    contractor_profile = relationship("ContractorProfile", back_populates="user")
    client_profile = relationship("ClientProfile", back_populates="user")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Location):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    service_type = Column(String)
    description = Column(String)
    status = Column(String, default="pending")
    
    client = relationship("User")
    contractor = relationship("ContractorProfile", secondary="order_contractors") 