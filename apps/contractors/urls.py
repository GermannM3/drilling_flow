from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractorReviewViewSet

router = DefaultRouter()
router.register(r'reviews', ContractorReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 