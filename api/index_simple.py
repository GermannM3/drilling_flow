from http.server import BaseHTTPRequestHandler
import json
import os

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
                    @media (max-width: 768px) {
                        .card {
                            flex: 1 1 100%;
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
        if self.path.startswith('/webhook'):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('OK'.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode()) 