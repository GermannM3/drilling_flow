from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from apps.contractors.models import ContractorProfile
from apps.notifications.utils import send_telegram_notification, send_sms

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    При изменении статуса заказа отправляем уведомления.
    Если заказ подтвержден – уведомление подрядчику (через Telegram, если доступен chat_id).
    Если заказ выполнен – уведомление клиенту (например, SMS).
    """
    if not created:
        # Если заказ назначен подрядчику
        if instance.status == 'confirmed':
            contractor = instance.assigned_contractor
            # Предполагается, что у пользователя подрядчика хранится chat_id Telegram
            if contractor and hasattr(contractor.user, 'telegram_chat_id'):
                chat_id = contractor.user.telegram_chat_id
                send_telegram_notification(chat_id, f"Новый заказ назначен: {instance}")
        # Если заказ завершён, обновляем рейтинг и уведомляем клиента
        elif instance.status == 'completed' and instance.rating is not None:
            contractor = instance.assigned_contractor
            if contractor:
                # Обновляем рейтинг подрядчика (простейший пример: среднее старого рейтинга и новой оценки)
                contractor.rating = (contractor.rating + float(instance.rating)) / 2
                contractor.save()
            # Если у клиента имеется номер для SMS (например, client.profile.phone_number)
            if hasattr(instance.client, 'profile') and getattr(instance.client.profile, 'phone_number', None):
                phone = instance.client.profile.phone_number
                send_sms(phone, f"Ваш заказ выполнен. Оцените выполнение: {instance}")
                
@receiver(post_save, sender=Order)
def update_contractor_daily_orders(sender, instance, created, **kwargs):
    """
    Если заказ подтвержден, увеличиваем счетчик заказов у подрядчика.
    """
    if not created and instance.status == 'confirmed':
        contractor = instance.assigned_contractor
        if contractor:
            contractor.daily_orders_count += 1
            contractor.save() 