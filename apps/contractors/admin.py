from django.contrib import admin
from .models import ContractorReview

@admin.register(ContractorReview)
class ContractorReviewAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'rating', 'created_at') 