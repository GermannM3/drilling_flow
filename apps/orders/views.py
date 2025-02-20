from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer

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