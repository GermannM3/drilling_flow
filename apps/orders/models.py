from django.contrib.gis.db import models as geomodels
from django.contrib.auth.models import User
from django.db import models
from math import radians, sin, cos, sqrt, atan2
from apps.geo.models import Location

SERVICE_CHOICES = (
    ('drilling', 'Бурение'),
    ('sewer', 'Канализация'),
    ('repair', 'Ремонт скважин'),
)

ORDER_STATUS_CHOICES = (
    ('pending', 'Ожидает подтверждения'),
    ('confirmed', 'Подтвержден'),
    ('cancelled', 'Отменен'),
    ('completed', 'Выполнен'),
)

class Order(Location):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    photo = models.ImageField("Фото", upload_to='orders/photos/', blank=True, null=True)
    assigned_contractor = models.ForeignKey(
        'contractors.ContractorProfile', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='orders'
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    confirmed_at = models.DateTimeField("Подтвержден", null=True, blank=True)
    feedback = models.TextField("Отзыв", blank=True)
    rating = models.DecimalField("Оценка", max_digits=3, decimal_places=1, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.address}"

    def distance_to(self, lat, lon):
        """Вычисляет расстояние до указанной точки в километрах"""
        R = 6371  # Радиус Земли в км

        lat1, lon1 = radians(float(self.latitude)), radians(float(self.longitude))
        lat2, lon2 = radians(float(lat)), radians(float(lon))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance

    def nearby_contractors(self, radius=10):
        """Находит подрядчиков в радиусе N км"""
        from apps.contractors.models import ContractorProfile
        
        nearby = []
        for contractor in ContractorProfile.objects.all():
            if contractor.latitude and contractor.longitude:
                distance = self.distance_to(contractor.latitude, contractor.longitude)
                if distance <= radius:
                    nearby.append((contractor, distance))
        
        return sorted(nearby, key=lambda x: x[1]) 