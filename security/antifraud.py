from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from .models import User, Order, Feedback

# Константы для настройки антифрода
IP_THRESHOLD = 1
DEVICE_THRESHOLD = 1
ACTIVITY_THRESHOLD = 3
NEGATIVE_FEEDBACK_THRESHOLD = 3
FRAUD_THRESHOLD = -2

def check_user_reputation(user):
    """
    Проверяет репутацию пользователя на основе различных факторов.
    Возвращает числовой показатель репутации.
    """
    reputation_score = 0
    
    try:
        # 1. Проверка IP
        if User.objects.filter(ip_address=user.ip_address).count() > IP_THRESHOLD:
            reputation_score -= 1
        
        # 2. Проверка устройства
        if User.objects.filter(device_id=user.device_id).count() > DEVICE_THRESHOLD:
            reputation_score -= 1
        
        # 3. Проверка активности
        recent_orders = Order.objects.filter(
            client=user,
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        if recent_orders > ACTIVITY_THRESHOLD:
            reputation_score -= 1
        
        # 4. Проверка отзывов
        negative_feedback = Feedback.objects.filter(
            contractor__user=user,
            rating__lt=NEGATIVE_FEEDBACK_THRESHOLD
        ).count()
        if negative_feedback > 0:
            reputation_score -= 1
    
    except Exception as e:
        # Логируем ошибку и возвращаем нейтральное значение
        print(f"Ошибка при проверке репутации пользователя {user.id}: {e}")
        return 0
    
    return reputation_score

def block_suspicious_users():
    """
    Блокирует пользователей с низким показателем репутации.
    """
    try:
        suspicious_users = User.objects.annotate(
            reputation_score=check_user_reputation()
        ).filter(reputation_score__lt=FRAUD_THRESHOLD)
        
        for user in suspicious_users:
            user.is_active = False
            user.save()
            print(f"Пользователь {user.id} заблокирован за подозрительную активность.")
    
    except Exception as e:
        print(f"Ошибка при блокировке пользователей: {e}")