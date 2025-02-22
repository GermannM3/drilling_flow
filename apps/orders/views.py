from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import OrderForm

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(client=self.request.user)
        from .tasks import distribute_order
        distribute_order.delay(order.id)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = self.queryset.filter(client=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def nearby_contractors(self, request, pk=None):
        order = self.get_object()
        radius = float(request.query_params.get('radius', 10))
        
        contractors = order.nearby_contractors(radius=radius)
        data = [{
            'id': c[0].id,
            'name': c[0].name,
            'distance': round(c[1], 2),
            'rating': c[0].rating
        } for c in contractors]
        
        return Response(data)

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/create_order.html'
    success_url = reverse_lazy('orders:order_success')

    def form_valid(self, form):
        order = form.save(commit=False)
        order.client = self.request.user
        order.save()
        # Запуск задачи распределения заказа через Celery
        from .tasks import distribute_order
        distribute_order.delay(order.id)
        return super().form_valid(form)

def order_success(request):
    return render(request, 'orders/order_success.html') 