from django.http import HttpResponseForbidden
from contractors.models import ContractorProfile

class MultiAccountCheckMiddleware:
    """
    Простая проверка: если с одного IP зарегистрировано более одного аккаунта подрядчика,
    выводим предупреждение в лог. При необходимости можно заблокировать выполнение запроса.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip:
            count = ContractorProfile.objects.filter(registration_ip=ip).count()
            if count > 1:
                # Здесь можно заблокировать запрос, если обнаружен мультиаккаунт.
                # Пример: возвращаем 403 Forbidden.
                # return HttpResponseForbidden("Мультиаккаунтинг запрещен")
                # Пока выводим предупреждение в консоль.
                print(f"Warning: Несколько подрядчиков зарегистрированы с IP: {ip}")
        response = self.get_response(request)
        return response 