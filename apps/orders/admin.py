from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_type', 'address', 'status', 'client')
    list_filter = ('status', 'service_type') 