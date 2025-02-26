"""
Order service for managing orders and contractors
"""
from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderRating
from app.models.user import User, ContractorProfile
from app.schemas.base import ServiceTypeEnum, OrderStatus
from app.utils.geo import calculate_distance

class OrderService:
    """Service for managing orders"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_order(
        self,
        client_id: str,
        service_type: ServiceTypeEnum,
        address: str,
        description: str,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        price: Optional[float] = None
    ) -> Order:
        """Create new order"""
        order = Order(
            client_id=client_id,
            service_type=service_type,
            address=address,
            description=description,
            location_lat=location_lat,
            location_lon=location_lon,
            price=price,
            status=OrderStatus.NEW
        )
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
    
    async def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return await self.session.get(Order, order_id)
    
    async def get_client_orders(self, client_id: str) -> List[Order]:
        """Get all orders for client"""
        result = await self.session.execute(
            select(Order)
            .where(Order.client_id == client_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_contractor_orders(self, contractor_id: str) -> List[Order]:
        """Get all orders for contractor"""
        result = await self.session.execute(
            select(Order)
            .where(Order.contractor_id == contractor_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def find_contractors(self, order: Order, limit: int = 5) -> List[User]:
        """
        Find suitable contractors for order
        
        Args:
            order: Order to find contractors for
            limit: Maximum number of contractors to return
            
        Returns:
            List of contractors sorted by rating and distance
        """
        # Get all active contractors with matching specialization
        query = select(User).join(ContractorProfile).where(
            and_(
                User.role == "contractor",
                ContractorProfile.is_available == True,
                ContractorProfile.specializations.contains([order.service_type.value])
            )
        )
        
        result = await self.session.execute(query)
        contractors = result.scalars().all()
        
        # Filter and sort contractors
        suitable = []
        for contractor in contractors:
            if not contractor.location_lat or not contractor.location_lon:
                continue
                
            # Calculate distance
            distance = calculate_distance(
                lat1=order.location_lat,
                lon1=order.location_lon,
                lat2=contractor.location_lat,
                lon2=contractor.location_lon
            ) if order.location_lat and order.location_lon else None
            
            # Check if within work radius
            profile = await self.session.get(ContractorProfile, contractor.id)
            if distance and profile.work_radius_km and distance > profile.work_radius_km:
                continue
            
            # Calculate score based on rating and distance
            score = contractor.rating or 0
            if distance:
                score = score / (distance + 1)  # Add 1 to avoid division by zero
            
            suitable.append((contractor, score))
        
        # Sort by score and limit
        suitable.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in suitable[:limit]]
    
    async def assign_contractor(self, order_id: int, contractor_id: str) -> bool:
        """
        Assign contractor to order
        
        Returns:
            bool: True if assigned successfully, False if already assigned
        """
        order = await self.get_order(order_id)
        if not order or order.contractor_id or order.status != OrderStatus.NEW:
            return False
            
        order.contractor_id = contractor_id
        order.status = OrderStatus.ASSIGNED
        await self.session.commit()
        return True
    
    async def complete_order(
        self,
        order_id: int,
        rating: Optional[float] = None,
        comment: Optional[str] = None
    ) -> Order:
        """Complete order and optionally add rating"""
        order = await self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
            
        order.status = OrderStatus.COMPLETED
        
        if rating:
            order_rating = OrderRating(
                order_id=order_id,
                rating=rating,
                comment=comment
            )
            self.session.add(order_rating)
            
            # Update contractor rating
            contractor = await self.session.get(User, order.contractor_id)
            if contractor:
                # Calculate new rating as average
                result = await self.session.execute(
                    select(OrderRating)
                    .join(Order)
                    .where(Order.contractor_id == contractor.id)
                )
                ratings = result.scalars().all()
                contractor.rating = sum(r.rating for r in ratings) / len(ratings)
        
        await self.session.commit()
        await self.session.refresh(order)
        return order 