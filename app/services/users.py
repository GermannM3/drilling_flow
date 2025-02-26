"""
User service for managing users and contractors
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, ContractorProfile
from app.schemas.base import UserRoleEnum
from app.core.database import get_async_session

class UserService:
    """Service for managing users"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user(self, telegram_id: str) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_user(
        self,
        telegram_id: str,
        username: str,
        first_name: str
    ) -> tuple[User, bool]:
        """
        Get existing user or create new one
        
        Returns:
            tuple[User, bool]: (user, is_new)
        """
        user = await self.get_user(telegram_id)
        if user:
            return user, False
            
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            role=UserRoleEnum.CLIENT
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user, True
    
    async def get_contractor_profile(self, user_id: int) -> Optional[ContractorProfile]:
        """Get contractor profile by user ID"""
        result = await self.session.execute(
            select(ContractorProfile).where(ContractorProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_contractor_profile(
        self,
        user_id: int,
        company_name: Optional[str] = None,
        description: Optional[str] = None,
        specializations: list[str] = None,
        work_radius_km: Optional[float] = None
    ) -> ContractorProfile:
        """Create contractor profile for user"""
        # Update user role
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
            
        user.role = UserRoleEnum.CONTRACTOR
        
        # Create profile
        profile = ContractorProfile(
            user_id=user_id,
            company_name=company_name,
            description=description,
            specializations=specializations or [],
            work_radius_km=work_radius_km
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def update_contractor_profile(
        self,
        profile_id: int,
        **kwargs
    ) -> ContractorProfile:
        """Update contractor profile"""
        profile = await self.session.get(ContractorProfile, profile_id)
        if not profile:
            raise ValueError("Profile not found")
            
        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
                
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def toggle_contractor_status(self, profile_id: int) -> bool:
        """Toggle contractor availability status"""
        profile = await self.session.get(ContractorProfile, profile_id)
        if not profile:
            raise ValueError("Profile not found")
            
        profile.is_available = not profile.is_available
        await self.session.commit()
        return profile.is_available 