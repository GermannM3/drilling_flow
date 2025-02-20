from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ContractorReview
from .serializers import ContractorReviewSerializer

class ContractorReviewViewSet(viewsets.ModelViewSet):
    queryset = ContractorReview.objects.all()
    serializer_class = ContractorReviewSerializer
    permission_classes = [IsAuthenticated] 