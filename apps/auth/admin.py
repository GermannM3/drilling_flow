from django.contrib import admin
from .models import User, ContractorProfile, ClientProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'telegram_id', 'phone', 'is_verified')}),
    )

@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'rating', 'current_load')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address') 