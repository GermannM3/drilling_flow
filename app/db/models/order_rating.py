from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class OrderRating(Base):
    __tablename__ = "order_ratings"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    contractor_id = Column(Integer, ForeignKey("users.id"))
    client_rating = Column(Float, nullable=True)
    contractor_rating = Column(Float, nullable=True)
    
    order = relationship("Order", back_populates="ratings")
    contractor = relationship("User", back_populates="contractor_ratings") 