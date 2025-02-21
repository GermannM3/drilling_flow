from rest_framework import viewsets
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer

class PaymentViewSet(viewsets.ViewSet):
    def create(self, request):
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        # Заглушка обработки платежа
        transaction = Transaction.objects.create(
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            status='completed'
        )
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data) 