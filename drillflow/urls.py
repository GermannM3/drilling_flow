from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.auth.urls')),
    path('api/contractors/', include('apps.contractors.urls')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
] 