/**
 * DrillFlow Web Application JavaScript
 */

// Глобальный объект для утилит DrillFlow
window.drillflowUtils = {};

document.addEventListener('DOMContentLoaded', function() {
    console.log('DrillFlow Web Application Initialized');
    
    // Инициализация компонентов
    initNotifications();
    initMobileMenu();
    initAnimations();
    
    // Обработка ошибок загрузки ресурсов
    handleResourceErrors();

    // Анимация для карточек
    const cards = document.querySelectorAll('.hover\\:scale-105, .hover\\:-translate-y-2');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('scale-105');
            if (this.classList.contains('hover\\:-translate-y-2')) {
                this.style.transform = 'translateY(-8px) scale(1.05)';
            }
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('scale-105');
            if (this.classList.contains('hover\\:-translate-y-2')) {
                this.style.transform = '';
            }
        });
    });

    // Добавляем эффект нажатия для всех кнопок и ссылок
    const buttons = document.querySelectorAll('.bg-blue-600, .bg-emerald-600, a[href], button');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.classList.add('scale-95');
            this.style.transition = 'all 0.1s ease';
        });
        
        button.addEventListener('mouseup', function() {
            this.classList.remove('scale-95');
            setTimeout(() => {
                this.style.transition = 'all 0.3s ease';
            }, 100);
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('scale-95');
        });
        
        // Добавляем эффект пульсации при наведении
        button.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 15px rgba(59, 130, 246, 0.5)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });

    // Анимация для иконок при наведении
    const icons = document.querySelectorAll('.material-symbols-outlined');
    icons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'rotate(180deg) scale(1.2)';
            this.style.transition = 'all 0.5s ease';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // Обработка уведомлений
    const notifications = document.querySelector('.animate-pulse');
    if (notifications) {
        notifications.addEventListener('click', function() {
            // Анимация при клике на уведомления
            this.classList.add('scale-125');
            setTimeout(() => {
                this.classList.remove('scale-125');
            }, 300);
        });
    }

    // Анимация для деталей (выпадающих меню)
    const details = document.querySelectorAll('details');
    details.forEach(detail => {
        detail.addEventListener('toggle', function() {
            const summary = this.querySelector('summary');
            if (this.open) {
                summary.classList.add('bg-blue-500/20');
            } else {
                summary.classList.remove('bg-blue-500/20');
            }
        });
    });

    // Функция для создания заказа
    window.createOrder = async function() {
        try {
            // Анимация загрузки
            const button = document.querySelector('#createOrderBtn');
            if (button) {
                button.innerHTML = '<span class="animate-spin inline-block mr-2">⟳</span> Создание...';
                button.disabled = true;
            }
            
            const response = await fetch('/api/orders/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: 'Новый заказ',
                    description: 'Описание заказа',
                    location: 'Адрес'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Order created:', data);
                
                // Показываем уведомление об успехе
                showNotification('Заказ успешно создан!', 'success');
                
                // Перенаправление на страницу заказа
                setTimeout(() => {
                    window.location.href = `/orders/${data.id}`;
                }, 1000);
            } else {
                console.error('Error creating order');
                showNotification('Ошибка при создании заказа', 'error');
                
                if (button) {
                    button.innerHTML = 'Создать заказ';
                    button.disabled = false;
                }
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Произошла ошибка', 'error');
            
            const button = document.querySelector('#createOrderBtn');
            if (button) {
                button.innerHTML = 'Создать заказ';
                button.disabled = false;
            }
        }
    };
    
    // Добавляем обработчики для кнопок создания заказа
    const createOrderBtns = document.querySelectorAll('[data-action="create-order"]');
    createOrderBtns.forEach(btn => {
        btn.addEventListener('click', createOrder);
    });
    
    // Добавляем атрибут data-action ко всем кнопкам создания заказа
    const createBtns = document.querySelectorAll('button:not([data-action])');
    createBtns.forEach(btn => {
        if (btn.textContent.trim().includes('Создать заказ') || 
            btn.textContent.trim().includes('Новый заказ')) {
            btn.setAttribute('data-action', 'create-order');
            btn.id = 'createOrderBtn';
        }
    });
});

/**
 * Инициализация уведомлений
 */
function initNotifications() {
    // Экспортируем функцию showNotification в глобальный объект drillflowUtils
    window.drillflowUtils.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="material-symbols-outlined">${type === 'error' ? 'error' : type === 'success' ? 'check_circle' : 'info'}</span>
                <p>${message}</p>
                <button class="close-btn">×</button>
            </div>
        `;
        document.body.appendChild(notification);
        
        // Добавляем обработчик для закрытия
        const closeBtn = notification.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.remove();
            });
        }
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000);
    };
    
    // Находим все элементы уведомлений
    const notifications = document.querySelectorAll('.notification');
    
    // Добавляем обработчики для закрытия уведомлений
    notifications.forEach(notification => {
        const closeBtn = notification.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            });
        }
        
        // Автоматическое закрытие через 5 секунд
        if (notification.classList.contains('auto-close')) {
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 5000);
        }
    });
}

/**
 * Инициализация мобильного меню
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
}

/**
 * Инициализация анимаций
 */
function initAnimations() {
    // Анимация появления элементов при прокрутке
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        // Функция проверки видимости элемента
        const isElementInViewport = (el) => {
            const rect = el.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        };
        
        // Функция для анимации элементов в поле зрения
        const animateElementsInViewport = () => {
            animatedElements.forEach(element => {
                if (isElementInViewport(element)) {
                    element.classList.add('animated');
                }
            });
        };
        
        // Запускаем анимацию при загрузке и прокрутке
        animateElementsInViewport();
        window.addEventListener('scroll', animateElementsInViewport);
    }
}

/**
 * Обработка ошибок загрузки ресурсов
 */
function handleResourceErrors() {
    // Обработка ошибок загрузки изображений
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/webapp/images/placeholder.png';
            this.alt = 'Изображение недоступно';
            
            // Используем глобальную функцию для уведомления
            if (window.drillflowUtils && window.drillflowUtils.showNotification) {
                window.drillflowUtils.showNotification('Некоторые изображения не могут быть загружены', 'info');
            }
        });
    });
    
    // Проверка доступности API
    function checkApiStatus() {
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                if (data.status !== 'ok') {
                    showOfflineNotification();
                }
            })
            .catch(() => {
                showOfflineNotification();
            });
    }
    
    // Показать уведомление о проблемах с соединением
    function showOfflineNotification() {
        // Используем глобальную функцию для уведомления
        if (window.drillflowUtils && window.drillflowUtils.showNotification) {
            window.drillflowUtils.showNotification('Проблемы с подключением к серверу. Некоторые функции могут быть недоступны.', 'error');
        } else {
            // Запасной вариант, если глобальная функция недоступна
            const notification = document.createElement('div');
            notification.className = 'notification error';
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="material-symbols-outlined">error</span>
                    <p>Проблемы с подключением к серверу. Некоторые функции могут быть недоступны.</p>
                    <button class="close-btn">×</button>
                </div>
            `;
            document.body.appendChild(notification);
            
            // Добавляем обработчик для закрытия
            const closeBtn = notification.querySelector('.close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    notification.remove();
                });
            }
        }
    }
    
    // Проверяем статус API при загрузке
    checkApiStatus();
}

/**
 * Утилиты для работы с формами
 */
const FormUtils = {
    /**
     * Валидация формы
     * @param {HTMLFormElement} form - Форма для валидации
     * @returns {boolean} - Результат валидации
     */
    validateForm: function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showError(field, 'Это поле обязательно для заполнения');
                isValid = false;
            } else {
                this.clearError(field);
            }
        });
        
        return isValid;
    },
    
    /**
     * Показать сообщение об ошибке для поля
     * @param {HTMLElement} field - Поле с ошибкой
     * @param {string} message - Сообщение об ошибке
     */
    showError: function(field, message) {
        // Удаляем существующее сообщение об ошибке, если оно есть
        this.clearError(field);
        
        // Создаем элемент с сообщением об ошибке
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        
        // Добавляем класс ошибки к полю
        field.classList.add('error');
        
        // Вставляем сообщение после поля
        field.parentNode.insertBefore(errorElement, field.nextSibling);
    },
    
    /**
     * Очистить сообщение об ошибке для поля
     * @param {HTMLElement} field - Поле для очистки ошибки
     */
    clearError: function(field) {
        // Удаляем класс ошибки
        field.classList.remove('error');
        
        // Находим и удаляем сообщение об ошибке
        const errorElement = field.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }
}; 