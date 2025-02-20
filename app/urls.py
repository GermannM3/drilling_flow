from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
] 