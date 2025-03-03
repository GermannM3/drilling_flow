require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { PrismaClient } = require('@prisma/client');
const createBot = require('./bot/bot');
const WebSocket = require('ws');
const session = require('express-session');
const TelegramLogin = require('node-telegram-login');

const prisma = new PrismaClient();
const app = express();
const wss = new WebSocket.Server({ noServer: true });

// Telegram Login widget settings
const telegramLogin = new TelegramLogin(process.env.TELEGRAM_BOT_TOKEN);

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true
}));
app.use(express.json());
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    maxAge: 1000 * 60 * 60 * 24 * 7 // 7 days
  }
}));

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
      
      switch(data.type) {
        case 'ORDER_UPDATE':
          await handleOrderUpdate(data.payload);
          broadcastEvent('ORDER_UPDATED', data.payload);
          break;
        case 'USER_UPDATE':
          await handleUserUpdate(data.payload);
          broadcastEvent('USER_UPDATED', data.payload);
          break;
        case 'SUBSCRIPTION_UPDATE':
          await handleSubscriptionUpdate(data.payload);
          broadcastEvent('SUBSCRIPTION_UPDATED', data.payload);
          break;
        case 'PAYMENT_UPDATE':
          await handlePaymentUpdate(data.payload);
          broadcastEvent('PAYMENT_UPDATED', data.payload);
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

// Telegram Login verification
app.post('/api/auth/telegram', async (req, res) => {
  try {
    const loginData = req.body;
    const isValid = telegramLogin.checkLoginData(loginData);

    if (!isValid) {
      return res.status(401).json({ error: 'Invalid authentication data' });
    }

    let user = await prisma.user.findFirst({
      where: { telegramId: BigInt(loginData.id) }
    });

    if (!user) {
      user = await prisma.user.create({
        data: {
          telegramId: BigInt(loginData.id),
          firstName: loginData.first_name,
          lastName: loginData.last_name || '',
          username: loginData.username || '',
          photoUrl: loginData.photo_url || ''
        }
      });
    }

    req.session.user = {
      id: user.id,
      telegramId: user.telegramId.toString(),
      firstName: user.firstName
    };

    res.json({ user });
  } catch (error) {
    console.error('Auth error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
});

// Функция для рассылки событий
function broadcastEvent(type, payload) {
  const message = JSON.stringify({ type, payload });
  for (const client of clients.values()) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  }
}

// Обработчики событий
async function handleOrderUpdate(payload) {
  await prisma.order.update({
    where: { id: payload.id },
    data: payload.data
  });
}

async function handleUserUpdate(payload) {
  await prisma.user.update({
    where: { id: payload.id },
    data: payload.data
  });
}

async function handleSubscriptionUpdate(payload) {
  await prisma.subscription.update({
    where: { id: payload.id },
    data: payload.data
  });
}

async function handlePaymentUpdate(payload) {
  await prisma.payment.update({
    where: { id: payload.id },
    data: payload.data
  });
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

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Получен сигнал SIGTERM, закрываем соединения...');
  await prisma.$disconnect();
  process.exit(0);
}); 