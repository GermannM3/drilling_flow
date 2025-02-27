/**
 * Основной JavaScript файл для веб-интерфейса DrillFlow
 */

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

/**
 * Инициализация приложения
 */
async function initApp() {
    console.log('DrillFlow Web Interface initialized');
    
    // Загружаем данные статистики
    loadDashboardStats();
    
    // Настраиваем обработчики событий для навигации
    setupNavigation();
    
    // Инициализируем формы
    setupForms();
}

/**
 * Загрузка статистики для панели управления
 */
async function loadDashboardStats() {
    try {
        // Получаем элементы для обновления
        const contractorsElement = document.getElementById('active-contractors');
        const clientsElement = document.getElementById('active-clients');
        const projectsElement = document.getElementById('completed-projects');
        const revenueElement = document.getElementById('total-revenue');
        
        // Если элементы найдены, загружаем данные
        if (contractorsElement || clientsElement || projectsElement || revenueElement) {
            const response = await window.DrillFlowAPI.getStats();
            
            if (response.status === 'ok') {
                const stats = response.stats;
                
                // Обновляем данные на странице
                if (contractorsElement) contractorsElement.textContent = stats.active_contractors;
                if (clientsElement) clientsElement.textContent = stats.active_clients;
                if (projectsElement) projectsElement.textContent = stats.projects_completed;
                if (revenueElement) revenueElement.textContent = formatCurrency(stats.total_revenue);
                
                console.log('Dashboard stats loaded successfully');
            } else {
                console.error('Failed to load stats:', response);
            }
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

/**
 * Настройка навигации
 */
function setupNavigation() {
    // Находим все элементы навигации
    const navItems = document.querySelectorAll('.sidebar-link');
    
    // Добавляем обработчики событий для навигации
    navItems.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Получаем идентификатор страницы
            const targetId = this.getAttribute('data-target');
            
            // Переключаем активные элементы навигации
            navItems.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
            
            // Загружаем контент для выбранной страницы
            loadPageContent(targetId);
        });
    });
    
    // Инициализируем страницу по умолчанию
    const defaultPage = document.querySelector('.sidebar-link.active') || navItems[0];
    if (defaultPage) {
        defaultPage.click();
    }
}

/**
 * Загрузка контента для выбранной страницы
 * @param {string} pageId Идентификатор страницы
 */
async function loadPageContent(pageId) {
    console.log('Loading page content for:', pageId);
    
    // Находим все контейнеры страниц
    const pageContainers = document.querySelectorAll('.page-container');
    
    // Скрываем все страницы
    pageContainers.forEach(container => {
        container.style.display = 'none';
    });
    
    // Показываем выбранную страницу
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.style.display = 'block';
        
        // Загружаем данные для конкретной страницы
        if (pageId === 'orders-page') {
            await loadOrders();
        } else if (pageId === 'users-page') {
            await loadUsers();
        } else if (pageId === 'stats-page') {
            await loadDetailedStats();
        }
    } else {
        console.error('Page not found:', pageId);
    }
}

/**
 * Загрузка списка заказов
 */
async function loadOrders() {
    try {
        const ordersContainer = document.getElementById('orders-list');
        if (!ordersContainer) return;
        
        // Очищаем контейнер
        ordersContainer.innerHTML = '<div class="loader">Загрузка данных...</div>';
        
        // Получаем данные заказов
        const response = await window.DrillFlowAPI.getOrders();
        
        if (response.status === 'ok') {
            const orders = response.orders;
            
            // Очищаем контейнер
            ordersContainer.innerHTML = '';
            
            if (orders.length === 0) {
                ordersContainer.innerHTML = '<div class="empty-state">Нет активных заказов</div>';
                return;
            }
            
            // Добавляем заказы в список
            orders.forEach(order => {
                const orderElement = document.createElement('div');
                orderElement.className = `order-item status-${order.status}`;
                orderElement.innerHTML = `
                    <div class="order-header">
                        <h3>${order.title}</h3>
                        <span class="order-status">${getStatusLabel(order.status)}</span>
                    </div>
                    <div class="order-details">
                        <p><strong>ID:</strong> ${order.id}</p>
                        <p><strong>Заказчик:</strong> ID ${order.client_id}</p>
                        <p><strong>Подрядчик:</strong> ${order.contractor_id ? 'ID ' + order.contractor_id : 'Не назначен'}</p>
                    </div>
                    <div class="order-actions">
                        <button class="btn btn-primary" onclick="showOrderDetails(${order.id})">Подробнее</button>
                    </div>
                `;
                ordersContainer.appendChild(orderElement);
            });
            
            console.log('Orders loaded successfully');
        } else {
            ordersContainer.innerHTML = '<div class="error-state">Ошибка загрузки данных</div>';
            console.error('Failed to load orders:', response);
        }
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

/**
 * Получение метки статуса
 * @param {string} status Статус заказа
 * @returns {string} Метка статуса
 */
function getStatusLabel(status) {
    const statusMap = {
        'active': 'Активен',
        'pending': 'В ожидании',
        'completed': 'Завершен',
        'cancelled': 'Отменен'
    };
    
    return statusMap[status] || status;
}

/**
 * Загрузка списка пользователей
 */
async function loadUsers() {
    try {
        const usersContainer = document.getElementById('users-list');
        if (!usersContainer) return;
        
        // Очищаем контейнер
        usersContainer.innerHTML = '<div class="loader">Загрузка данных...</div>';
        
        // Получаем данные пользователей
        const response = await window.DrillFlowAPI.getUsers();
        
        if (response.status === 'ok') {
            const users = response.users;
            
            // Очищаем контейнер
            usersContainer.innerHTML = '';
            
            if (users.length === 0) {
                usersContainer.innerHTML = '<div class="empty-state">Нет пользователей</div>';
                return;
            }
            
            // Добавляем пользователей в список
            users.forEach(user => {
                const userElement = document.createElement('div');
                userElement.className = `user-item role-${user.role}`;
                userElement.innerHTML = `
                    <div class="user-header">
                        <h3>${user.name}</h3>
                        <span class="user-role">${getRoleLabel(user.role)}</span>
                    </div>
                    <div class="user-details">
                        <p><strong>ID:</strong> ${user.id}</p>
                        <p><strong>Email:</strong> ${user.email}</p>
                    </div>
                    <div class="user-actions">
                        <button class="btn btn-primary" onclick="showUserDetails(${user.id})">Подробнее</button>
                    </div>
                `;
                usersContainer.appendChild(userElement);
            });
            
            console.log('Users loaded successfully');
        } else {
            usersContainer.innerHTML = '<div class="error-state">Ошибка загрузки данных</div>';
            console.error('Failed to load users:', response);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

/**
 * Получение метки роли
 * @param {string} role Роль пользователя
 * @returns {string} Метка роли
 */
function getRoleLabel(role) {
    const roleMap = {
        'admin': 'Администратор',
        'contractor': 'Подрядчик',
        'client': 'Заказчик'
    };
    
    return roleMap[role] || role;
}

/**
 * Загрузка детальной статистики
 */
async function loadDetailedStats() {
    // Реализация загрузки детальной статистики
    console.log('Loading detailed stats...');
}

/**
 * Настройка форм
 */
function setupForms() {
    // Находим форму создания заказа
    const createOrderForm = document.getElementById('create-order-form');
    
    // Добавляем обработчик события отправки формы
    if (createOrderForm) {
        createOrderForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            // Получаем данные формы
            const formData = new FormData(createOrderForm);
            const orderData = {
                title: formData.get('title'),
                status: 'pending',
                client_id: parseInt(formData.get('client_id')),
                contractor_id: formData.get('contractor_id') ? parseInt(formData.get('contractor_id')) : null
            };
            
            try {
                // Отправляем данные на сервер
                const response = await window.DrillFlowAPI.createOrder(orderData);
                
                if (response.status === 'success') {
                    // Очищаем форму
                    createOrderForm.reset();
                    
                    // Показываем сообщение об успехе
                    alert('Заказ успешно создан!');
                    
                    // Обновляем список заказов
                    loadOrders();
                } else {
                    alert('Ошибка создания заказа: ' + response.message);
                }
            } catch (error) {
                console.error('Error creating order:', error);
                alert('Произошла ошибка при создании заказа');
            }
        });
    }
}

/**
 * Форматирование валюты
 * @param {number} value Значение
 * @returns {string} Форматированное значение
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('ru-RU', { 
        style: 'currency', 
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

/**
 * Отображение деталей заказа
 * @param {number} orderId ID заказа
 */
function showOrderDetails(orderId) {
    alert(`Просмотр деталей заказа ${orderId}`);
    // TODO: Реализовать отображение деталей заказа
}

/**
 * Отображение деталей пользователя
 * @param {number} userId ID пользователя
 */
function showUserDetails(userId) {
    alert(`Просмотр деталей пользователя ${userId}`);
    // TODO: Реализовать отображение деталей пользователя
}

// Глобальные функции
window.showOrderDetails = showOrderDetails;
window.showUserDetails = showUserDetails; 