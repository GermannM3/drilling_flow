from django.db import models
from django.db.models import F, ExpressionWrapper, FloatField

class OrderManager(models.Manager):
    def nearby(self, lat, lon, radius=10):
        """Находит заказы в радиусе N километров"""
        R = 6371  # Радиус Земли в км
        
        # Используем формулу гаверсинусов
        distance = ExpressionWrapper(
            R * 2 * models.functions.ACos(
                models.functions.Cos(models.functions.Radians(lat)) *
                models.functions.Cos(models.functions.Radians(F('latitude'))) *
                models.functions.Cos(models.functions.Radians(F('longitude')) - 
                                   models.functions.Radians(lon)) +
                models.functions.Sin(models.functions.Radians(lat)) *
                models.functions.Sin(models.functions.Radians(F('latitude')))
            ),
            output_field=FloatField()
        )
        
        return self.annotate(distance=distance).filter(distance__lte=radius) 