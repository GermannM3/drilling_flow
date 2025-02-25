/**
 * Файл для проверки доступности статических файлов в среде Vercel
 */

// Функция для проверки доступности статических файлов
function checkStaticFiles() {
    console.log('Проверка доступности статических файлов...');
    
    // Проверяем доступность изображения-заглушки
    const img = new Image();
    img.onload = function() {
        console.log('Изображение-заглушка доступно');
        if (window.drillflowUtils && window.drillflowUtils.showNotification) {
            window.drillflowUtils.showNotification('Статические файлы доступны', 'success');
        }
    };
    img.onerror = function() {
        console.error('Ошибка загрузки изображения-заглушки');
        if (window.drillflowUtils && window.drillflowUtils.showNotification) {
            window.drillflowUtils.showNotification('Ошибка загрузки статических файлов', 'error');
        }
    };
    img.src = '/static/webapp/images/placeholder.png';
    
    // Проверяем доступность стилей
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/webapp/style.css';
    link.onload = function() {
        console.log('Стили доступны');
    };
    link.onerror = function() {
        console.error('Ошибка загрузки стилей');
        if (window.drillflowUtils && window.drillflowUtils.showNotification) {
            window.drillflowUtils.showNotification('Ошибка загрузки стилей', 'error');
        }
    };
    document.head.appendChild(link);
    
    // Проверяем доступность скриптов
    const script = document.createElement('script');
    script.src = '/static/webapp/script.js';
    script.onload = function() {
        console.log('Скрипты доступны');
    };
    script.onerror = function() {
        console.error('Ошибка загрузки скриптов');
        if (window.drillflowUtils && window.drillflowUtils.showNotification) {
            window.drillflowUtils.showNotification('Ошибка загрузки скриптов', 'error');
        }
    };
    document.head.appendChild(script);
}

// Экспортируем функцию для использования в других файлах
window.drillflowUtils = window.drillflowUtils || {};
window.drillflowUtils.checkStaticFiles = checkStaticFiles;

// Запускаем проверку при загрузке страницы
document.addEventListener('DOMContentLoaded', checkStaticFiles); 