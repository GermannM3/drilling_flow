from django.contrib.gis.db import models as geomodels
from django.contrib.auth.models import User

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

class Order(geomodels.Model):
    client = geomodels.ForeignKey(User, on_delete=geomodels.CASCADE, related_name='orders')
    service_type = geomodels.CharField("Услуга", max_length=20, choices=SERVICE_CHOICES)
    address = geomodels.CharField("Адрес", max_length=255)
    location = geomodels.PointField("Геолокация", null=True, blank=True)
    description = geomodels.TextField("Описание", blank=True)
    photo = geomodels.ImageField("Фото", upload_to='orders/photos/', blank=True, null=True)
    assigned_contractor = geomodels.ForeignKey(
        'contractors.ContractorProfile', null=True, blank=True,
        on_delete=geomodels.SET_NULL, related_name='orders'
    )
    created_at = geomodels.DateTimeField("Создан", auto_now_add=True)
    confirmed_at = geomodels.DateTimeField("Подтвержден", null=True, blank=True)
    status = geomodels.CharField("Статус", max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    feedback = geomodels.TextField("Отзыв", blank=True)
    rating = geomodels.DecimalField("Оценка", max_digits=3, decimal_places=1, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.address}" 