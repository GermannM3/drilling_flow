from django.contrib import admin
from .models import ContractorReview, ContractorProfile

@admin.register(ContractorReview)
class ContractorReviewAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'rating', 'created_at')

@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'work_radius', 'verified', 'rating')
    list_filter = ('verified', 'specialization') 