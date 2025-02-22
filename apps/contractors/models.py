from django.db import models
from django.contrib.auth.models import User
from apps.geo.models import Location

SPECIALIZATION_CHOICES = (
    ('drilling', 'Бурение'),
    ('sewer', 'Канализация'),
    ('repair', 'Ремонт скважин'),
)

class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contractor_profile')
    full_name = models.CharField("ФИО", max_length=255)
    contact = models.CharField("Контакты", max_length=255)
    specialization = models.CharField("Специализация", max_length=20, choices=SPECIALIZATION_CHOICES)
    work_radius = models.DecimalField("Радиус работы (км)", max_digits=5, decimal_places=2)  # Обычно до 100 км
    documents = models.FileField("Документы", upload_to='contractors/documents/', blank=True, null=True)
    verified = models.BooleanField("Верифицирован", default=False)
    max_daily_orders = models.PositiveIntegerField("Максимум заказов в день", default=3)
    daily_orders_count = models.PositiveIntegerField("Заказы за сегодня", default=0)
    rating = models.DecimalField("Рейтинг", max_digits=4, decimal_places=2, default=0.0)
    registration_ip = models.GenericIPAddressField("IP адрес", blank=True, null=True)
    device_info = models.CharField("Информация об устройстве", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.full_name

class ContractorReview(models.Model):
    contractor = models.ForeignKey(ContractorProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.contractor.user.username}: {self.rating}"

class ContractorLocation(Location):
    contractor = models.OneToOneField('ContractorProfile', on_delete=models.CASCADE)
    service_radius = models.DecimalField(max_digits=5, decimal_places=2) 