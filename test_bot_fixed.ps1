# PowerShell-скрипт для тестирования Telegram-бота на локальном сервере
# Убедитесь, что сервер запущен на порту 3001 (node local_test_bot.js)

$webhookUrl = "http://localhost:3001/webhook"

# Функция для отправки команды боту
function Send-BotCommand {
    param (
        [string]$Command,
        [int]$UserId = 1234567,
        [string]$FirstName = "Тест",
        [string]$Username = "testuser"
    )

    $body = @{
        update_id = 123456789
        message = @{
            message_id = 123
            from = @{
                id = $UserId
                first_name = $FirstName
                username = $Username
            }
            chat = @{
                id = $UserId
                first_name = $FirstName
                username = $Username
                type = "private"
            }
            date = [int][double]::Parse((Get-Date -UFormat %s))
            text = $Command
        }
    } | ConvertTo-Json -Depth 10

    Write-Host "Отправка команды: $Command" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $body -ContentType "application/json"
        Write-Host "Ответ от сервера: $response" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Host "Ошибка при отправке запроса: $_" -ForegroundColor Red
        return $null
    }
}

# Функция для вывода меню команд
function Show-CommandMenu {
    Write-Host "`nДоступные команды для тестирования:`n" -ForegroundColor Cyan
    Write-Host "1. /start - Запуск бота"
    Write-Host "2. Профиль - Просмотр профиля"
    Write-Host "3. Заказы - Просмотр заказов"
    Write-Host "4. Обновить статус - Обновление статуса"
    Write-Host "5. Статистика - Просмотр статистики"
    Write-Host "6. Доход - Финансовая информация"
    Write-Host "7. Настройки - Настройки профиля"
    Write-Host "8. Подписка - Управление подпиской"
    Write-Host "9. Тестовый платеж - Тестирование оплаты"
    Write-Host "10. Помощь - Справка по боту"
    Write-Host "0. Выход из программы тестирования`n"
}

# Проверяем доступность сервера
try {
    $testResponse = Invoke-RestMethod -Uri "http://localhost:3001" -Method Get -TimeoutSec 3
    Write-Host "Сервер доступен: $($testResponse.status)" -ForegroundColor Green
}
catch {
    Write-Host "ОШИБКА: Сервер недоступен! Убедитесь, что локальный сервер запущен." -ForegroundColor Red
    Write-Host "Запустите сервер командой: node local_test_bot.js" -ForegroundColor Yellow
    exit
}

# Главный цикл программы
Write-Host "=== Тестирование Telegram-бота DrillFlow ===" -ForegroundColor Cyan
Write-Host "Сервер: $webhookUrl" -ForegroundColor Cyan

while ($true) {
    Show-CommandMenu
    $choice = Read-Host "Выберите команду (0-10)"
    
    switch ($choice) {
        "0" { 
            Write-Host "Завершение программы тестирования..." -ForegroundColor Yellow
            exit 
        }
        "1" { Send-BotCommand -Command "/start" }
        "2" { Send-BotCommand -Command "📋 Профиль" }
        "3" { Send-BotCommand -Command "📦 Заказы" }
        "4" { Send-BotCommand -Command "🔄 Обновить статус" }
        "5" { Send-BotCommand -Command "📊 Статистика" }
        "6" { Send-BotCommand -Command "💰 Доход" }
        "7" { Send-BotCommand -Command "⚙️ Настройки" }
        "8" { Send-BotCommand -Command "🔄 Подписка" }
        "9" { Send-BotCommand -Command "💳 Тестовый платеж" }
        "10" { Send-BotCommand -Command "❓ Помощь" }
        default { Write-Host "Неверный выбор. Пожалуйста, выберите число от 0 до 10." -ForegroundColor Red }
    }
    
    # Пауза перед следующим запросом
    Start-Sleep -Seconds 1
} 