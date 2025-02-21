from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.auth.urls')),
    path('api/contractors/', include('apps.contractors.urls', namespace='contractors')),
    path('api/clients/', include('apps.clients.urls')),
    path('api/orders/', include('apps.orders.urls', namespace='orders')),
    path('api/payments/', include('apps.payments.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 