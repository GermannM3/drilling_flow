from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import uuid
# Создаем заглушку для Stripe
# import stripe

# Инициализируем Stripe API (заглушка)
stripe_api_key = os.getenv("STRIPE_API_KEY", "")
# stripe.api_key = stripe_api_key

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Если запрос на корневой путь, возвращаем HTML-страницу
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>DrillFlow - Платформа для управления буровыми работами</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        background-color: #f5f5f5;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    header {
                        background-color: #2c3e50;
                        color: white;
                        padding: 20px 0;
                        text-align: center;
                    }
                    .logo {
                        font-size: 2.5rem;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }
                    .tagline {
                        font-size: 1.2rem;
                        opacity: 0.8;
                    }
                    .main {
                        display: flex;
                        flex-wrap: wrap;
                        margin-top: 30px;
                        gap: 20px;
                    }
                    .card {
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        padding: 25px;
                        flex: 1 1 300px;
                        margin-bottom: 20px;
                    }
                    .card h2 {
                        color: #2c3e50;
                        margin-top: 0;
                        border-bottom: 2px solid #f1c40f;
                        padding-bottom: 10px;
                    }
                    .card ul {
                        padding-left: 20px;
                    }
                    .card li {
                        margin-bottom: 10px;
                    }
                    .cta {
                        text-align: center;
                        margin: 40px 0;
                    }
                    .button {
                        display: inline-block;
                        background-color: #f1c40f;
                        color: #2c3e50;
                        padding: 12px 30px;
                        border-radius: 30px;
                        text-decoration: none;
                        font-weight: bold;
                        font-size: 1.1rem;
                        transition: all 0.3s ease;
                    }
                    .button:hover {
                        background-color: #e67e22;
                        transform: translateY(-2px);
                    }
                    .status {
                        background-color: #e8f5e9;
                        border-left: 4px solid #4caf50;
                        padding: 15px;
                        margin-bottom: 20px;
                        border-radius: 4px;
                    }
                    .status.error {
                        background-color: #ffebee;
                        border-left-color: #f44336;
                    }
                    footer {
                        background-color: #2c3e50;
                        color: white;
                        text-align: center;
                        padding: 20px 0;
                        margin-top: 40px;
                    }
                    .payment-options {
                        text-align: center;
                        margin: 30px 0;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }
                    .subscription-options {
                        text-align: center;
                        margin: 30px 0;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }
                    .payment-buttons {
                        display: flex;
                        justify-content: center;
                        gap: 20px;
                        margin-top: 15px;
                    }
                    .payment-button {
                        display: inline-block;
                        background-color: #3498db;
                        color: white;
                        padding: 10px 25px;
                        border-radius: 30px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: all 0.3s ease;
                    }
                    .payment-button:hover {
                        background-color: #2980b9;
                        transform: translateY(-2px);
                    }
                    .subscription-button {
                        display: inline-block;
                        background-color: #27ae60;
                        color: white;
                        padding: 10px 25px;
                        border-radius: 30px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: all 0.3s ease;
                    }
                    .subscription-button:hover {
                        background-color: #2ecc71;
                        transform: translateY(-2px);
                    }
                    .modal {
                        display: none;
                        position: fixed;
                        z-index: 1;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        overflow: auto;
                        background-color: rgba(0,0,0,0.4);
                    }
                    .modal-content {
                        background-color: #fefefe;
                        margin: 15% auto;
                        padding: 20px;
                        border: 1px solid #888;
                        width: 80%;
                        max-width: 500px;
                        border-radius: 8px;
                    }
                    .close {
                        color: #aaa;
                        float: right;
                        font-size: 28px;
                        font-weight: bold;
                    }
                    .close:hover,
                    .close:focus {
                        color: black;
                        text-decoration: none;
                        cursor: pointer;
                    }
                    .form-group {
                        margin-bottom: 15px;
                    }
                    .form-group label {
                        display: block;
                        margin-bottom: 5px;
                        font-weight: bold;
                    }
                    .form-group input {
                        width: 100%;
                        padding: 8px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                    }
                    .form-submit {
                        background-color: #2ecc71;
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: bold;
                    }
                    .form-submit:hover {
                        background-color: #27ae60;
                    }
                    .subscription-features {
                        text-align: left;
                        max-width: 500px;
                        margin: 0 auto;
                        padding: 15px;
                        background-color: #f9f9f9;
                        border-radius: 8px;
                        margin-bottom: 20px;
                    }
                    .subscription-features h3 {
                        color: #2c3e50;
                        border-bottom: 1px solid #ddd;
                        padding-bottom: 5px;
                    }
                    .subscription-features ul {
                        padding-left: 25px;
                    }
                    .subscription-price {
                        display: inline-block;
                        background-color: #2c3e50;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 30px;
                        margin: 10px 0;
                        font-weight: bold;
                    }
                    @media (max-width: 768px) {
                        .card {
                            flex: 1 1 100%;
                        }
                        .payment-buttons {
                            flex-direction: column;
                            gap: 10px;
                        }
                    }
                </style>
            </head>
            <body>
                <header>
                    <div class="container">
                        <div class="logo">DrillFlow</div>
                        <div class="tagline">Платформа для управления буровыми работами</div>
                    </div>
                </header>
                
                <div class="container">
                    <div class="status">
                        <strong>Статус:</strong> Сервер работает. Бот активен и готов к использованию.
                    </div>
                    
                    <div class="main">
                        <div class="card">
                            <h2>Для заказчиков</h2>
                            <ul>
                                <li>Размещайте заказы на буровые работы</li>
                                <li>Отслеживайте статус выполнения</li>
                                <li>Получайте уведомления о ходе работ</li>
                                <li>Оценивайте качество выполненных работ</li>
                            </ul>
                        </div>
                        
                        <div class="card">
                            <h2>Для подрядчиков</h2>
                            <ul>
                                <li>Находите новые заказы</li>
                                <li>Управляйте своим расписанием</li>
                                <li>Отчитывайтесь о выполненных работах</li>
                                <li>Получайте рейтинг и отзывы</li>
                            </ul>
                        </div>
                        
                        <div class="card">
                            <h2>Возможности платформы</h2>
                            <ul>
                                <li>Автоматическое распределение заказов</li>
                                <li>Система рейтингов и отзывов</li>
                                <li>Уведомления в реальном времени</li>
                                <li>Аналитика и отчеты</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="payment-options">
                        <h2>Тестирование платежей</h2>
                        <p>Вы можете протестировать функционал платежей через наши платежные системы:</p>
                        <div class="payment-buttons">
                            <a href="#" class="payment-button" id="paymaster-button">PayMaster Test</a>
                            <a href="#" class="payment-button" id="redsys-button">Redsys Test</a>
                        </div>
                    </div>
                    
                    <div class="subscription-options">
                        <h2>Оформление подписки</h2>
                        <p>Оформите подписку для доступа к полному функционалу платформы</p>
                        
                        <div class="subscription-features">
                            <h3>Включено в подписку:</h3>
                            <ul>
                                <li>Неограниченное количество заказов</li>
                                <li>Доступ к расширенной аналитике</li>
                                <li>Приоритетная техническая поддержка</li>
                                <li>Отсутствие комиссий за сделки</li>
                            </ul>
                            <div class="subscription-price">499 руб/месяц</div>
                        </div>
                        
                        <div class="payment-buttons">
                            <a href="#" class="subscription-button" id="paymaster-subscription-button">Подписка через PayMaster</a>
                            <a href="#" class="subscription-button" id="redsys-subscription-button">Подписка через Redsys</a>
                        </div>
                    </div>
                    
                    <!-- Модальное окно для платежей PayMaster -->
                    <div id="paymaster-modal" class="modal">
                        <div class="modal-content">
                            <span class="close paymaster-close">&times;</span>
                            <h2>Тестовый платеж через PayMaster</h2>
                            <p>Заполните форму для совершения тестового платежа:</p>
                            <form id="paymaster-form">
                                <div class="form-group">
                                    <label for="paymaster-name">Ваше имя:</label>
                                    <input type="text" id="paymaster-name" required>
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-phone">Телефон:</label>
                                    <input type="tel" id="paymaster-phone" required>
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-email">Email:</label>
                                    <input type="email" id="paymaster-email" required>
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-amount">Сумма (RUB):</label>
                                    <input type="number" id="paymaster-amount" value="500" readonly>
                                </div>
                                <button type="submit" class="form-submit">Оплатить</button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Модальное окно для платежей Redsys -->
                    <div id="redsys-modal" class="modal">
                        <div class="modal-content">
                            <span class="close redsys-close">&times;</span>
                            <h2>Тестовый платеж через Redsys</h2>
                            <p>Заполните форму для совершения тестового платежа:</p>
                            <form id="redsys-form">
                                <div class="form-group">
                                    <label for="redsys-name">Ваше имя:</label>
                                    <input type="text" id="redsys-name" required>
                                </div>
                                <div class="form-group">
                                    <label for="redsys-phone">Телефон:</label>
                                    <input type="tel" id="redsys-phone" required>
                                </div>
                                <div class="form-group">
                                    <label for="redsys-email">Email:</label>
                                    <input type="email" id="redsys-email" required>
                                </div>
                                <div class="form-group">
                                    <label for="redsys-amount">Сумма (RUB):</label>
                                    <input type="number" id="redsys-amount" value="500" readonly>
                                </div>
                                <button type="submit" class="form-submit">Оплатить</button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Модальное окно для подписки через PayMaster -->
                    <div id="paymaster-subscription-modal" class="modal">
                        <div class="modal-content">
                            <span class="close paymaster-subscription-close">&times;</span>
                            <h2>Оформление подписки через PayMaster</h2>
                            <p>Заполните данные для оформления подписки:</p>
                            <form id="paymaster-subscription-form">
                                <div class="form-group">
                                    <label for="paymaster-subscription-name">Ваше имя:</label>
                                    <input type="text" id="paymaster-subscription-name" required>
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-subscription-phone">Телефон:</label>
                                    <input type="tel" id="paymaster-subscription-phone" required>
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-subscription-email">Email:</label>
                                    <input type="email" id="paymaster-subscription-email" required>
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-subscription-telegram">ID Telegram (опционально):</label>
                                    <input type="text" id="paymaster-subscription-telegram" placeholder="Ваш ID в Telegram">
                                </div>
                                <div class="form-group">
                                    <label for="paymaster-subscription-amount">Стоимость подписки (RUB):</label>
                                    <input type="number" id="paymaster-subscription-amount" value="499" readonly>
                                </div>
                                <button type="submit" class="form-submit">Оформить подписку</button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Модальное окно для подписки через Redsys -->
                    <div id="redsys-subscription-modal" class="modal">
                        <div class="modal-content">
                            <span class="close redsys-subscription-close">&times;</span>
                            <h2>Оформление подписки через Redsys</h2>
                            <p>Заполните данные для оформления подписки:</p>
                            <form id="redsys-subscription-form">
                                <div class="form-group">
                                    <label for="redsys-subscription-name">Ваше имя:</label>
                                    <input type="text" id="redsys-subscription-name" required>
                                </div>
                                <div class="form-group">
                                    <label for="redsys-subscription-phone">Телефон:</label>
                                    <input type="tel" id="redsys-subscription-phone" required>
                                </div>
                                <div class="form-group">
                                    <label for="redsys-subscription-email">Email:</label>
                                    <input type="email" id="redsys-subscription-email" required>
                                </div>
                                <div class="form-group">
                                    <label for="redsys-subscription-telegram">ID Telegram (опционально):</label>
                                    <input type="text" id="redsys-subscription-telegram" placeholder="Ваш ID в Telegram">
                                </div>
                                <div class="form-group">
                                    <label for="redsys-subscription-amount">Стоимость подписки (RUB):</label>
                                    <input type="number" id="redsys-subscription-amount" value="499" readonly>
                                </div>
                                <button type="submit" class="form-submit">Оформить подписку</button>
                            </form>
                        </div>
                    </div>

                    <div class="cta">
                        <a href="https://t.me/Drill_Flow_bot" class="button">Начать работу с ботом</a>
                    </div>
                    
                    <div class="card">
                        <h2>API Endpoints</h2>
                        <ul>
                            <li><a href="/health">/health</a> - Проверка работоспособности</li>
                            <li><a href="/debug">/debug</a> - Отладочная информация</li>
                            <li><a href="/webhook">/webhook</a> - Информация о вебхуке</li>
                            <li><a href="/set-webhook">/set-webhook</a> - Установка вебхука</li>
                        </ul>
                    </div>
                </div>
                
                <footer>
                    <div class="container">
                        <p>DrillFlow &copy; 2024. Все права защищены.</p>
                    </div>
                </footer>
                
                <script>
                    // Обработка модальных окон для платежей
                    document.addEventListener('DOMContentLoaded', function() {
                        // PayMaster modal
                        const paymasterButton = document.getElementById('paymaster-button');
                        const paymasterModal = document.getElementById('paymaster-modal');
                        const paymasterClose = document.querySelector('.paymaster-close');
                        const paymasterForm = document.getElementById('paymaster-form');
                        
                        // Redsys modal
                        const redsysButton = document.getElementById('redsys-button');
                        const redsysModal = document.getElementById('redsys-modal');
                        const redsysClose = document.querySelector('.redsys-close');
                        const redsysForm = document.getElementById('redsys-form');
                        
                        // PayMaster events
                        paymasterButton.addEventListener('click', function() {
                            paymasterModal.style.display = 'block';
                        });
                        
                        paymasterClose.addEventListener('click', function() {
                            paymasterModal.style.display = 'none';
                        });
                        
                        paymasterForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            const paymentId = generatePaymentId();
                            const name = document.getElementById('paymaster-name').value;
                            const phone = document.getElementById('paymaster-phone').value;
                            const email = document.getElementById('paymaster-email').value;
                            
                            // Отправка данных на сервер
                            fetch('/process-payment', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    provider: 'PayMaster',
                                    name: name,
                                    phone: phone,
                                    email: email,
                                    amount: 500
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                alert(`Спасибо, ${name}! В реальной среде вы были бы перенаправлены на страницу оплаты PayMaster. ID платежа: ${data.payment_id}`);
                                paymasterModal.style.display = 'none';
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('Произошла ошибка при обработке платежа. Пожалуйста, попробуйте позже.');
                            });
                        });
                        
                        // Redsys events
                        redsysButton.addEventListener('click', function() {
                            redsysModal.style.display = 'block';
                        });
                        
                        redsysClose.addEventListener('click', function() {
                            redsysModal.style.display = 'none';
                        });
                        
                        redsysForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            const name = document.getElementById('redsys-name').value;
                            const phone = document.getElementById('redsys-phone').value;
                            const email = document.getElementById('redsys-email').value;
                            
                            // Отправка данных на сервер
                            fetch('/process-payment', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    provider: 'Redsys',
                                    name: name,
                                    phone: phone,
                                    email: email,
                                    amount: 500
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                alert(`Спасибо, ${name}! В реальной среде вы были бы перенаправлены на страницу оплаты Redsys. ID платежа: ${data.payment_id}`);
                                redsysModal.style.display = 'none';
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('Произошла ошибка при обработке платежа. Пожалуйста, попробуйте позже.');
                            });
                        });
                        
                        // Закрытие модальных окон при клике вне их области
                        window.addEventListener('click', function(event) {
                            if (event.target == paymasterModal) {
                                paymasterModal.style.display = 'none';
                            }
                            if (event.target == redsysModal) {
                                redsysModal.style.display = 'none';
                            }
                        });
                        
                        // Генерация уникального ID платежа
                        function generatePaymentId() {
                            return 'test_' + Math.random().toString(36).substr(2, 9);
                        }
                    });

                    // Обработка модальных окон для подписки
                    document.addEventListener('DOMContentLoaded', function() {
                        // PayMaster subscription modal
                        const paymasterSubscriptionButton = document.getElementById('paymaster-subscription-button');
                        const paymasterSubscriptionModal = document.getElementById('paymaster-subscription-modal');
                        const paymasterSubscriptionClose = document.querySelector('.paymaster-subscription-close');
                        const paymasterSubscriptionForm = document.getElementById('paymaster-subscription-form');
                        
                        // Redsys subscription modal
                        const redsysSubscriptionButton = document.getElementById('redsys-subscription-button');
                        const redsysSubscriptionModal = document.getElementById('redsys-subscription-modal');
                        const redsysSubscriptionClose = document.querySelector('.redsys-subscription-close');
                        const redsysSubscriptionForm = document.getElementById('redsys-subscription-form');
                        
                        // PayMaster subscription events
                        paymasterSubscriptionButton.addEventListener('click', function() {
                            paymasterSubscriptionModal.style.display = 'block';
                        });
                        
                        paymasterSubscriptionClose.addEventListener('click', function() {
                            paymasterSubscriptionModal.style.display = 'none';
                        });
                        
                        paymasterSubscriptionForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            const name = document.getElementById('paymaster-subscription-name').value;
                            const phone = document.getElementById('paymaster-subscription-phone').value;
                            const email = document.getElementById('paymaster-subscription-email').value;
                            const telegramId = document.getElementById('paymaster-subscription-telegram').value;
                            
                            // Отправка данных на сервер
                            fetch('/process-subscription', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    provider: 'PayMaster',
                                    name: name,
                                    phone: phone,
                                    email: email,
                                    telegram_id: telegramId,
                                    amount: 499
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                alert(`Спасибо, ${name}! Ваша подписка через PayMaster успешно оформлена. ID подписки: ${data.subscription_id}`);
                                paymasterSubscriptionModal.style.display = 'none';
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('Произошла ошибка при обработке подписки. Пожалуйста, попробуйте позже.');
                            });
                        });
                        
                        // Redsys subscription events
                        redsysSubscriptionButton.addEventListener('click', function() {
                            redsysSubscriptionModal.style.display = 'block';
                        });
                        
                        redsysSubscriptionClose.addEventListener('click', function() {
                            redsysSubscriptionModal.style.display = 'none';
                        });
                        
                        redsysSubscriptionForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            const name = document.getElementById('redsys-subscription-name').value;
                            const phone = document.getElementById('redsys-subscription-phone').value;
                            const email = document.getElementById('redsys-subscription-email').value;
                            const telegramId = document.getElementById('redsys-subscription-telegram').value;
                            
                            // Отправка данных на сервер
                            fetch('/process-subscription', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    provider: 'Redsys',
                                    name: name,
                                    phone: phone,
                                    email: email,
                                    telegram_id: telegramId,
                                    amount: 499
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                alert(`Спасибо, ${name}! Ваша подписка через Redsys успешно оформлена. ID подписки: ${data.subscription_id}`);
                                redsysSubscriptionModal.style.display = 'none';
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('Произошла ошибка при обработке подписки. Пожалуйста, попробуйте позже.');
                            });
                        });
                        
                        // Закрытие модальных окон при клике вне их области
                        window.addEventListener('click', function(event) {
                            if (event.target == redsysModal) {
                                redsysModal.style.display = 'none';
                            }
                            if (event.target == paymasterSubscriptionModal) {
                                paymasterSubscriptionModal.style.display = 'none';
                            }
                            if (event.target == redsysSubscriptionModal) {
                                redsysSubscriptionModal.style.display = 'none';
                            }
                        });
                    });
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        # Если запрос на API, возвращаем JSON
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {
                "app": "DrillFlow Bot",
                "version": "1.0.0",
                "status": "running",
                "webhook_url": f"https://{os.getenv('BOT_WEBHOOK_DOMAIN', 'drilling-flow.vercel.app')}/webhook",
                "telegram_bot": "@Drill_Flow_bot"
            }
            
            self.wfile.write(json.dumps(response_data).encode())
        
    def do_POST(self):
        # Обработка пути /process-payment для симуляции обработки платежей с веб-интерфейса
        if self.path == "/process-payment":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payment_data = json.loads(post_data.decode())
            
            # Генерируем ID платежа
            payment_id = str(uuid.uuid4())
            
            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "payment_id": payment_id,
                "message": f"Тестовый платеж через {payment_data.get('provider', 'неизвестный провайдер')} успешно обработан"
            }
            
            self.wfile.write(json.dumps(response).encode())
        # Обработка пути /process-subscription для создания подписки
        elif self.path == "/process-subscription":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            subscription_data = json.loads(post_data.decode())
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Получаем провайдера оплаты
            provider = subscription_data.get('provider', 'PayMaster')
            
            try:
                # Генерируем ID подписки
                subscription_id = str(uuid.uuid4())
                
                # Имитируем создание подписки через выбранного провайдера
                if provider == 'Redsys':
                    # Иммитация подписки через Redsys
                    response = {
                        "status": "success",
                        "subscription_id": f"redsys_{subscription_id}",
                        "provider": "Redsys",
                        "customer_name": subscription_data.get("name", ""),
                        "customer_email": subscription_data.get("email", ""),
                        "amount": 499,
                        "message": "Подписка через Redsys успешно оформлена"
                    }
                else:
                    # По умолчанию используем PayMaster
                    response = {
                        "status": "success",
                        "subscription_id": f"paymaster_{subscription_id}",
                        "provider": "PayMaster",
                        "customer_name": subscription_data.get("name", ""),
                        "customer_email": subscription_data.get("email", ""),
                        "amount": 499,
                        "message": "Подписка через PayMaster успешно оформлена"
                    }
                
                # Сохраняем информацию о подписке в лог
                print(f"Оформлена подписка: {response}")
                
                # Если указан Telegram ID, логируем его отдельно
                if subscription_data.get("telegram_id"):
                    telegram_id = subscription_data.get("telegram_id")
                    print(f"Подписка привязана к Telegram ID: {telegram_id}")
                    
            except Exception as e:
                response = {
                    "status": "error",
                    "message": f"Ошибка при создании подписки: {str(e)}"
                }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "error",
                "message": "Endpoint not found"
            }
            
            self.wfile.write(json.dumps(response).encode()) 