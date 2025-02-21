from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser

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

class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contractor_profile')
    specialization = models.CharField(max_length=50)
    work_radius = models.IntegerField()  # в км
    documents = models.JSONField(default=list, blank=True)
    rating = models.FloatField(default=0.0)
    max_load = models.IntegerField(default=3)  # макс. заказов в день
    current_load = models.IntegerField(default=0)
    geolocation = models.PointField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}" 