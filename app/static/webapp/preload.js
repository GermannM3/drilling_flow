/**
 * Файл для предварительной загрузки статических файлов
 * Используется в случае ошибок загрузки основных файлов
 */

// Функция для отображения уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Добавляем стили для уведомления
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 350px;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            animation: slideIn 0.3s ease-out forwards;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .notification-message {
            flex: 1;
            margin-right: 10px;
        }
        
        .notification-close {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: inherit;
            opacity: 0.7;
        }
        
        .notification-close:hover {
            opacity: 1;
        }
        
        .notification-info {
            background-color: #3b82f6;
            color: white;
        }
        
        .notification-error {
            background-color: #ef4444;
            color: white;
        }
        
        .notification-success {
            background-color: #10b981;
            color: white;
        }
    `;
    
    document.head.appendChild(style);
    
    // Автоматическое закрытие через 5 секунд
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
    
    // Обработчик для кнопки закрытия
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Добавляем анимацию выхода
    const styleOut = document.createElement('style');
    styleOut.textContent = `
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(styleOut);
}

// Функция для загрузки резервных стилей
function loadFallbackStyles() {
    const style = document.createElement('style');
    style.textContent = `
        body {
            line-height: inherit;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background: linear-gradient(135deg, #111827, #1e3a8a, #064e3b);
            font-family: 'Inter', sans-serif;
            color: #e0f2fe;
        }
        .container {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1, h2, h3 {
            color: #7dd3fc;
        }
        a {
            color: #38bdf8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .card {
            background: rgba(30, 58, 138, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            border: 2px solid rgba(59, 130, 246, 0.2);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            text-align: center;
            background-color: #3b82f6;
            color: white;
            cursor: pointer;
            border: none;
            transition: background-color 0.2s;
        }
        .btn:hover {
            background-color: #2563eb;
        }
        .btn-secondary {
            background-color: #4b5563;
        }
        .btn-secondary:hover {
            background-color: #374151;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-control {
            display: block;
            width: 100%;
            padding: 0.75rem;
            border-radius: 0.5rem;
            border: 2px solid rgba(59, 130, 246, 0.2);
            background: rgba(15, 23, 42, 0.5);
            color: #e0f2fe;
        }
        .form-control:focus {
            outline: none;
            border-color: #3b82f6;
        }
    `;
    document.head.appendChild(style);
    showNotification('Загружены резервные стили из-за проблем с основными файлами стилей', 'info');
}

// Экспортируем функции для использования в других файлах
window.drillflowUtils = {
    showNotification,
    loadFallbackStyles
}; 