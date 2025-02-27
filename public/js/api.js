/**
 * Клиент API для DrillFlow
 */

// Базовый URL для API
const API_BASE_URL = window.location.origin;

/**
 * Получение списка пользователей
 * @returns {Promise<Object>} Результат запроса с данными пользователей
 */
async function getUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching users:', error);
        throw error;
    }
}

/**
 * Получение списка заказов
 * @returns {Promise<Object>} Результат запроса с данными заказов
 */
async function getOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching orders:', error);
        throw error;
    }
}

/**
 * Получение статистики
 * @returns {Promise<Object>} Результат запроса с данными статистики
 */
async function getStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching stats:', error);
        throw error;
    }
}

/**
 * Создание нового заказа
 * @param {Object} orderData Данные заказа
 * @returns {Promise<Object>} Результат запроса с данными созданного заказа
 */
async function createOrder(orderData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        return await response.json();
    } catch (error) {
        console.error('Error creating order:', error);
        throw error;
    }
}

// Экспортируем функции
window.DrillFlowAPI = {
    getUsers,
    getOrders,
    getStats,
    createOrder
}; 