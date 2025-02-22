from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.geo.models import Location

class User(AbstractUser):
    ROLE_CHOICES = (
        ('contractor', 'Подрядчик'),
        ('client', 'Клиент'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telegram_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

class ContractorProfile(Location):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    services = models.JSONField(default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    specialization = models.CharField(max_length=50)
    work_radius = models.IntegerField()  # в км
    documents = models.JSONField(default=list, blank=True)
    max_load = models.IntegerField(default=3)  # макс. заказов в день
    current_load = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}" 