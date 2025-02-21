from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractorReviewViewSet, ContractorRegisterView

router = DefaultRouter()
router.register(r'reviews', ContractorReviewViewSet)

app_name = 'contractors'

urlpatterns = [
    path('', include(router.urls)),
    path('register/', ContractorRegisterView.as_view(), name='register'),
] 