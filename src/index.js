require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { PrismaClient } = require('@prisma/client');
const createBot = require('./bot/bot');
const WebSocket = require('ws');

const prisma = new PrismaClient();
const app = express();
const wss = new WebSocket.Server({ noServer: true });

// Middleware
app.use(cors());
app.use(express.json());

// Инициализация бота
const bot = createBot();

// WebSocket подключения
const clients = new Map();

wss.on('connection', (ws, req) => {
  const id = req.headers['sec-websocket-key'];
  clients.set(id, ws);

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message);
      
      // Обработка событий от веб-интерфейса
      switch(data.type) {
        case 'ORDER_UPDATE':
          // Обновляем заказ и уведомляем всех клиентов
          await handleOrderUpdate(data.payload);
          broadcastEvent('ORDER_UPDATED', data.payload);
          break;
        case 'USER_UPDATE':
          await handleUserUpdate(data.payload);
          broadcastEvent('USER_UPDATED', data.payload);
          break;
      }
    } catch (error) {
      console.error('WebSocket error:', error);
    }
  });

  ws.on('close', () => {
    clients.delete(id);
  });
});

// Функция для рассылки событий всем подключенным клиентам
function broadcastEvent(type, payload) {
  const message = JSON.stringify({ type, payload });
  for (const client of clients.values()) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  }
}

// Обработка ошибок
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Что-то пошло не так!');
});

// Создаем HTTP сервер
const server = app.listen(process.env.PORT || 3001, () => {
  console.log(`Server running on port ${process.env.PORT || 3001}`);
});

// Интегрируем WebSocket с HTTP сервером
server.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

// Обработчики событий
async function handleOrderUpdate(payload) {
  // Обновление заказа в базе данных
  await prisma.order.update({
    where: { id: payload.id },
    data: payload.data
  });
}

async function handleUserUpdate(payload) {
  // Обновление пользователя в базе данных
  await prisma.user.update({
    where: { id: payload.id },
    data: payload.data
  });
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Получен сигнал SIGTERM, закрываем соединения...');
  await prisma.$disconnect();
  process.exit(0);
}); 