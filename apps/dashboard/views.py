from django.shortcuts import render
from apps.orders.models import Order
from apps.auth.models import ContractorProfile
import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.contractors.models import Contractor
from apps.clients.models import Client
from django.conf import settings
from django.db.models import Avg
from apps.notifications.models import Notification

def dashboard_view(request):
    orders_count = Order.objects.count()
    top_contractors = ContractorProfile.objects.order_by('-rating')[:10]
    context = {
        'orders_count': orders_count,
        'top_contractors': top_contractors,
    }
    return render(request, 'dashboard.html', context)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика
        context['orders_count'] = Order.objects.count()
        context['contractors_count'] = Contractor.objects.filter(is_active=True).count()
        context['clients_count'] = Client.objects.count()
        context['completed_orders_count'] = Order.objects.filter(status='completed').count()
        context['pending_orders_count'] = Order.objects.filter(status='pending').count()
        context['avg_rating'] = Contractor.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Последние заказы
        context['recent_orders'] = Order.objects.select_related('client').order_by('-created_at')[:5]
        
        # Лучшие подрядчики
        context['top_contractors'] = Contractor.objects.order_by('-rating')[:5]
        
        # Уведомления
        context['notifications'] = Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        context['unread_notifications_count'] = context['notifications'].count()
        
        # Данные для карты
        orders_for_map = Order.objects.filter(latitude__isnull=False, longitude__isnull=False)
        orders_json = [{
            'id': order.id,
            'latitude': float(order.latitude),
            'longitude': float(order.longitude),
            'status': order.get_status_display()
        } for order in orders_for_map]
        context['orders_json'] = json.dumps(orders_json)
        
        # API ключ для Google Maps
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        
        return context 