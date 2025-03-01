"""
Модуль для работы с подписками Stripe.
"""
import os
import stripe
import json
import uuid
from loguru import logger
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализируем Stripe API
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Настройки подписки
SUBSCRIPTION_PRICE_ID = os.getenv("STRIPE_SUBSCRIPTION_PRICE_ID", "")
SUBSCRIPTION_PRODUCT_ID = os.getenv("STRIPE_SUBSCRIPTION_PRODUCT_ID", "")
SUBSCRIPTION_CURRENCY = "rub"  # Рубли
SUBSCRIPTION_AMOUNT = 49900  # 499 рублей в копейках

# Кэш для хранения информации о подписках пользователей
# {user_id: {"subscription_id": "...", "status": "active"}}
subscription_cache = {}

async def create_customer(user_id, email=None, name=None, metadata=None):
    """
    Создает нового клиента в Stripe или возвращает существующего.
    """
    try:
        # Метаданные для связи клиента с пользователем бота
        user_metadata = {"telegram_id": str(user_id)}
        if metadata:
            user_metadata.update(metadata)
        
        # Ищем клиента по telegram_id в метаданных
        existing_customers = stripe.Customer.list(
            limit=1,
            email=email,
            metadata={"telegram_id": str(user_id)}
        )
        
        if existing_customers and existing_customers.data:
            logger.info(f"Найден существующий клиент Stripe для пользователя {user_id}")
            return existing_customers.data[0]
        
        # Создаем нового клиента
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=user_metadata
        )
        logger.info(f"Создан новый клиент Stripe для пользователя {user_id}")
        return customer
    except Exception as e:
        logger.error(f"Ошибка при создании клиента в Stripe: {e}")
        raise

async def create_subscription_checkout_session(user_id, customer_id, success_url, cancel_url):
    """
    Создает сессию оформления подписки в Stripe.
    """
    try:
        # Создаем сессию оформления подписки
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": SUBSCRIPTION_PRICE_ID,
                "quantity": 1
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "telegram_id": str(user_id)
            }
        )
        
        logger.info(f"Создана сессия оформления подписки для пользователя {user_id}")
        return session
    except Exception as e:
        logger.error(f"Ошибка при создании сессии оформления подписки: {e}")
        raise

async def create_payment_link(user_id, customer_id):
    """
    Создает ссылку на оплату подписки в Stripe.
    """
    try:
        # Если ID цены подписки не найден, создаем новый продукт и цену
        if not SUBSCRIPTION_PRICE_ID:
            # Создаем продукт для подписки, если его еще нет
            product = stripe.Product.create(
                name="DrillFlow Месячная подписка",
                description="Доступ к расширенным функциям DrillFlow на 1 месяц",
                metadata={"type": "subscription"}
            )
            
            # Создаем цену для подписки
            price = stripe.Price.create(
                product=product.id,
                unit_amount=SUBSCRIPTION_AMOUNT,
                currency=SUBSCRIPTION_CURRENCY,
                recurring={"interval": "month"},
                metadata={"type": "subscription"}
            )
            price_id = price.id
        else:
            price_id = SUBSCRIPTION_PRICE_ID
        
        # Создаем платежную ссылку
        payment_link = stripe.PaymentLink.create(
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            application_fee_amount=0,
            after_completion={"type": "redirect", "redirect": {"url": "https://t.me/DrillFlowBot"}},
            customer=customer_id,
            metadata={"telegram_id": str(user_id)}
        )
        
        logger.info(f"Создана платежная ссылка для пользователя {user_id}")
        return payment_link
    except Exception as e:
        logger.error(f"Ошибка при создании платежной ссылки: {e}")
        raise

async def check_subscription_status(user_id, customer_id=None):
    """
    Проверяет статус подписки пользователя.
    """
    try:
        # Сначала проверяем кэш
        if user_id in subscription_cache:
            subscription_data = subscription_cache[user_id]
            try:
                # Проверяем актуальность кэша, запрашивая подписку из Stripe
                subscription = stripe.Subscription.retrieve(subscription_data["subscription_id"])
                subscription_cache[user_id]["status"] = subscription.status
                return subscription.status == "active"
            except Exception:
                # Если подписка не найдена, удаляем из кэша
                del subscription_cache[user_id]
        
        # Если клиент не передан, пытаемся найти его по telegram_id
        if not customer_id:
            customers = stripe.Customer.list(
                limit=1,
                metadata={"telegram_id": str(user_id)}
            )
            if not customers or not customers.data:
                logger.info(f"Клиент Stripe для пользователя {user_id} не найден")
                return False
            customer_id = customers.data[0].id
        
        # Получаем список активных подписок клиента
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1
        )
        
        if subscriptions and subscriptions.data:
            subscription = subscriptions.data[0]
            # Сохраняем в кэш
            subscription_cache[user_id] = {
                "subscription_id": subscription.id,
                "status": subscription.status
            }
            logger.info(f"Пользователь {user_id} имеет активную подписку")
            return True
        
        logger.info(f"Пользователь {user_id} не имеет активной подписки")
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса подписки: {e}")
        return False

async def handle_webhook_event(payload, signature):
    """
    Обрабатывает события от Stripe Webhook.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, stripe_webhook_secret
        )
        
        # Тип события
        event_type = event['type']
        logger.info(f"Получено событие от Stripe: {event_type}")
        
        # Обрабатываем разные типы событий
        if event_type == 'checkout.session.completed':
            # Сессия оформления подписки завершена
            session = event['data']['object']
            customer_id = session.get('customer')
            telegram_id = session.get('metadata', {}).get('telegram_id')
            
            if telegram_id:
                # Обновляем кэш подписок
                subscription_cache[telegram_id] = {
                    "status": "active"
                }
                logger.info(f"Подписка успешно оформлена для пользователя {telegram_id}")
        
        elif event_type == 'customer.subscription.created':
            # Создана новая подписка
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            
            # Находим пользователя по customer_id
            try:
                customer = stripe.Customer.retrieve(customer_id)
                telegram_id = customer.get('metadata', {}).get('telegram_id')
                
                if telegram_id:
                    # Обновляем кэш подписок
                    subscription_cache[telegram_id] = {
                        "subscription_id": subscription.id,
                        "status": subscription.status
                    }
                    logger.info(f"Создана новая подписка для пользователя {telegram_id}")
            except Exception as e:
                logger.error(f"Не удалось найти пользователя для customer_id {customer_id}: {e}")
        
        elif event_type == 'customer.subscription.updated':
            # Обновление статуса подписки
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            
            # Находим пользователя по customer_id
            try:
                customer = stripe.Customer.retrieve(customer_id)
                telegram_id = customer.get('metadata', {}).get('telegram_id')
                
                if telegram_id:
                    # Обновляем кэш подписок
                    subscription_cache[telegram_id] = {
                        "subscription_id": subscription.id,
                        "status": subscription.status
                    }
                    logger.info(f"Обновлен статус подписки для пользователя {telegram_id}: {subscription.status}")
            except Exception as e:
                logger.error(f"Не удалось найти пользователя для customer_id {customer_id}: {e}")
        
        elif event_type == 'customer.subscription.deleted':
            # Подписка удалена
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            
            # Находим пользователя по customer_id
            try:
                customer = stripe.Customer.retrieve(customer_id)
                telegram_id = customer.get('metadata', {}).get('telegram_id')
                
                if telegram_id and telegram_id in subscription_cache:
                    # Удаляем из кэша подписок
                    del subscription_cache[telegram_id]
                    logger.info(f"Подписка удалена для пользователя {telegram_id}")
            except Exception as e:
                logger.error(f"Не удалось найти пользователя для customer_id {customer_id}: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook события: {e}")
        return False 