from enum import Enum
from django.conf import settings

class PaymentProvider(Enum):
    YOOMONEY = 'yoomoney'
    SBP = 'sbp'
    STRIPE = 'stripe'

def create_payment(order: Order, provider: PaymentProvider):
    amount = order.total * 0.2  # 20% предоплата
    description = f"Заказ №{order.id} ({order.service_type})"
    
    if provider == PaymentProvider.YOOMONEY:
        payment = YooMoneyClient.create_payment(amount, description)
    elif provider == PaymentProvider.SBP:
        payment = SBPClient.create_payment(amount, description)
    elif provider == PaymentProvider.STRIPE:
        payment = StripeClient.create_payment(amount, description)
    else:
        raise ValueError("Unsupported payment provider")
    
    Payment.objects.create(
        order=order,
        provider=provider.value,
        amount=amount,
        external_id=payment.id,
        status='pending'
    )
    
    return payment.url

def handle_payment_webhook(request, provider: PaymentProvider):
    event = request.json()
    
    if provider == PaymentProvider.YOOMONEY:
        payment_id = event['operation_id']
        status = event['status']
    elif provider == PaymentProvider.STRIPE:
        payment_id = event['data']['object']['id']
        status = event['data']['object']['status']
    
    payment = Payment.objects.get(external_id=payment_id)
    payment.status = status
    payment.save()
    
    if status == 'succeeded':
        order = payment.order
        order.status = 'confirmed'
        order.save()
        notify_user(order.client, "Ваш заказ подтвержден!") 