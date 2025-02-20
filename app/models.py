from django.db import models
from django.contrib.auth.models import User

class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100, choices=(
        ('drilling', 'Бурение'),
        ('sewer', 'Канализация'),
    ))
    work_radius_km = models.IntegerField(default=100)
    max_daily_orders = models.IntegerField(default=2)
    current_orders = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    # Документы (например, лицензии) можно реализовать с помощью FileField

    def __str__(self):
        return self.full_name

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name

class Order(models.Model):
    SERVICE_CHOICES = (
        ('drilling', 'Бурение'),
        ('well_repair', 'Ремонт скважин'),
        ('sewer', 'Канализация'),
    )
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='order_photos/', null=True, blank=True)
    status = models.CharField(max_length=20, default='new')  # new, accepted, completed, cancelled
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Таймер подтверждения заказа (например, 5 минут) можно реализовать через фоновые задачи

    def __str__(self):
        return f"Заказ #{self.id} для услуги {self.get_service_type_display()}" 