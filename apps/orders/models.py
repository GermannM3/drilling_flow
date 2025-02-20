from django.contrib.gis.db import models
from apps.auth.models import User, ContractorProfile

class Order(models.Model):
    SERVICE_TYPES = (
        ('drilling', 'Бурение'),
        ('repair', 'Ремонт скважин'),
        ('sewerage', 'Канализация'),
    )
    STATUSES = (
        ('pending', 'Ожидает'),
        ('assigned', 'Назначен'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    )
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    address = models.CharField(max_length=255)
    geolocation = models.PointField()
    description = models.TextField(null=True, blank=True)
    photos = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.get_service_type_display()}" 