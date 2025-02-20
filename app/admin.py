from django.contrib import admin
from .models import ContractorProfile, ClientProfile, Order

@admin.register(ContractorProfile)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'rating', 'current_orders')

@admin.register(ClientProfile)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'contact')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'contractor', 'service_type', 'status', 'created_at') 