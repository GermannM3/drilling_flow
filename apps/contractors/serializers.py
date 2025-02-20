from rest_framework import serializers
from .models import ContractorReview

class ContractorReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorReview
        fields = '__all__' 