from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Contractor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('drilling', 'Бурение'),
        ('sewer', 'Канализация'),
        ('repair', 'Ремонт скважин')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    work_radius = models.PositiveIntegerField(help_text="Радиус работы в метрах")
    max_daily_orders = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    location = models.PointField(srid=4326, help_text="Геопозиция подрядчика")
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='contractor_docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['specialization']),
        ] 