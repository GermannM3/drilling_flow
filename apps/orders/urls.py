from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderCreateView, order_success

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

app_name = 'orders'

urlpatterns = [
    path('', include(router.urls)),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('success/', order_success, name='order_success'),
] 