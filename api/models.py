import os
import sys
import json
import enum
import time
from typing import List, Optional, Dict, Any

# Перечисления для различных статусов и типов

class ContractorStatus(enum.Enum):
    """Статус подрядчика в системе"""
    PENDING = "pending"  # Ожидает верификации
    ACTIVE = "active"    # Активный подрядчик
    BLOCKED = "blocked"  # Заблокирован
    DELETED = "deleted"  # Удален

class SpecializationType(enum.Enum):
    """Типы специализации подрядчиков"""
    DRILLING = "drilling"      # Бурение
    SEWERAGE = "sewerage"      # Канализация
    BOTH = "both"              # Оба типа работ

class VerificationStatus(enum.Enum):
    """Статусы верификации подрядчиков"""
    PENDING = "pending"        # Ожидает проверки
    APPROVED = "approved"      # Подтвержден
    REJECTED = "rejected"      # Отклонен

class OrderStatus(enum.Enum):
    """Статусы заказов"""
    CREATED = "created"        # Создан
    ASSIGNED = "assigned"      # Назначен подрядчику
    IN_PROGRESS = "in_progress"  # В процессе выполнения
    COMPLETED = "completed"    # Выполнен
    CANCELLED = "cancelled"    # Отменен
    FAILED = "failed"          # Не выполнен

# Модели данных

class User:
    """Модель данных пользователя"""
    def __init__(
        self,
        id: Optional[int] = None,
        telegram_id: Optional[str] = None,
        username: Optional[str] = None,
        full_name: str = "",
        phone: Optional[str] = None,
        email: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
        is_contractor: bool = False,
        work_radius: float = 50.0,
        max_orders_per_day: int = 2,
        current_orders: int = 0,
        rating: float = 5.0
    ):
        self.id = id
        self.telegram_id = telegram_id
        self.username = username
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.is_active = is_active
        self.is_verified = is_verified
        self.is_contractor = is_contractor
        self.work_radius = work_radius
        self.max_orders_per_day = max_orders_per_day
        self.current_orders = current_orders
        self.rating = rating
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сохранения в базе данных"""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_contractor": self.is_contractor,
            "work_radius": self.work_radius,
            "max_orders_per_day": self.max_orders_per_day,
            "current_orders": self.current_orders,
            "rating": self.rating
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Создает объект из словаря, полученного из базы данных"""
        return cls(
            id=data.get("id"),
            telegram_id=data.get("telegram_id"),
            username=data.get("username"),
            full_name=data.get("full_name", ""),
            phone=data.get("phone"),
            email=data.get("email"),
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            is_contractor=data.get("is_contractor", False),
            work_radius=data.get("work_radius", 50.0),
            max_orders_per_day=data.get("max_orders_per_day", 2),
            current_orders=data.get("current_orders", 0),
            rating=data.get("rating", 5.0)
        )

class Contractor:
    """Модель данных подрядчика"""
    def __init__(
        self,
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        name: str = "",
        rating: float = 5.0,
        orders_completed: int = 0,
        location: Optional[str] = None,
        specialization: SpecializationType = SpecializationType.DRILLING,
        status: ContractorStatus = ContractorStatus.PENDING
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.rating = rating
        self.orders_completed = orders_completed
        self.location = location
        self.specialization = specialization
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сохранения в базе данных"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "rating": self.rating,
            "orders_completed": self.orders_completed,
            "location": self.location,
            "specialization": self.specialization.value if isinstance(self.specialization, enum.Enum) else self.specialization,
            "status": self.status.value if isinstance(self.status, enum.Enum) else self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contractor':
        """Создает объект из словаря, полученного из базы данных"""
        specialization = data.get("specialization")
        if specialization and not isinstance(specialization, SpecializationType):
            try:
                specialization = SpecializationType(specialization)
            except ValueError:
                specialization = SpecializationType.DRILLING
        
        status = data.get("status")
        if status and not isinstance(status, ContractorStatus):
            try:
                status = ContractorStatus(status)
            except ValueError:
                status = ContractorStatus.PENDING
        
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            name=data.get("name", ""),
            rating=data.get("rating", 5.0),
            orders_completed=data.get("orders_completed", 0),
            location=data.get("location"),
            specialization=specialization or SpecializationType.DRILLING,
            status=status or ContractorStatus.PENDING
        )

class Order:
    """Модель данных заказа"""
    def __init__(
        self,
        id: Optional[int] = None,
        title: str = "",
        description: Optional[str] = None,
        location: Optional[str] = None,
        price: Optional[float] = None,
        status: OrderStatus = OrderStatus.CREATED,
        created_at: Optional[int] = None,
        updated_at: Optional[int] = None,
        customer_id: Optional[int] = None,
        contractor_id: Optional[int] = None,
        specialization: SpecializationType = SpecializationType.DRILLING,
        address: Optional[str] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.location = location
        self.price = price
        self.status = status
        self.created_at = created_at or int(time.time())
        self.updated_at = updated_at or int(time.time())
        self.customer_id = customer_id
        self.contractor_id = contractor_id
        self.specialization = specialization
        self.address = address
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сохранения в базе данных"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "price": self.price,
            "status": self.status.value if isinstance(self.status, enum.Enum) else self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "customer_id": self.customer_id,
            "contractor_id": self.contractor_id,
            "specialization": self.specialization.value if isinstance(self.specialization, enum.Enum) else self.specialization,
            "address": self.address
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Создает объект из словаря, полученного из базы данных"""
        status = data.get("status")
        if status and not isinstance(status, OrderStatus):
            try:
                status = OrderStatus(status)
            except ValueError:
                status = OrderStatus.CREATED
        
        specialization = data.get("specialization")
        if specialization and not isinstance(specialization, SpecializationType):
            try:
                specialization = SpecializationType(specialization)
            except ValueError:
                specialization = SpecializationType.DRILLING
        
        # Приводим created_at и updated_at к целым числам, если они представлены в другом формате
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            try:
                import datetime
                dt = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = int(dt.timestamp())
            except:
                created_at = int(time.time())
        
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            try:
                import datetime
                dt = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                updated_at = int(dt.timestamp())
            except:
                updated_at = int(time.time())
        
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description"),
            location=data.get("location"),
            price=data.get("price"),
            status=status or OrderStatus.CREATED,
            created_at=created_at,
            updated_at=updated_at,
            customer_id=data.get("customer_id"),
            contractor_id=data.get("contractor_id"),
            specialization=specialization or SpecializationType.DRILLING,
            address=data.get("address")
        )

class OrderRating:
    """Модель данных оценки заказа"""
    def __init__(
        self,
        id: Optional[int] = None,
        order_id: Optional[int] = None,
        contractor_id: Optional[int] = None,
        client_rating: Optional[float] = None,
        contractor_rating: Optional[float] = None,
        rating: Optional[float] = None
    ):
        self.id = id
        self.order_id = order_id
        self.contractor_id = contractor_id
        self.client_rating = client_rating
        self.contractor_rating = contractor_rating
        self.rating = rating
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь для сохранения в базе данных"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "contractor_id": self.contractor_id,
            "client_rating": self.client_rating,
            "contractor_rating": self.contractor_rating,
            "rating": self.rating
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderRating':
        """Создает объект из словаря, полученного из базы данных"""
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id"),
            contractor_id=data.get("contractor_id"),
            client_rating=data.get("client_rating"),
            contractor_rating=data.get("contractor_rating"),
            rating=data.get("rating")
        )

# Вспомогательные функции для работы с моделями будут добавлены позже
# в отдельном слое доступа к данным (data access layer) 