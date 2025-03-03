const express = require('express');
const jwt = require('jsonwebtoken');

// Middleware для проверки JWT токена
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Требуется авторизация' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Недействительный токен' });
    }
    req.user = user;
    next();
  });
};

// Middleware для проверки прав администратора
const requireAdmin = async (req, res, next) => {
  try {
    const user = await req.prisma.user.findUnique({
      where: { id: req.user.id }
    });

    if (user?.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Доступ запрещен' });
    }

    next();
  } catch (error) {
    next(error);
  }
};

// Настройка маршрутов
function setupWebRoutes(app, prisma) {
  // Внедряем Prisma в запрос
  app.use((req, res, next) => {
    req.prisma = prisma;
    next();
  });

  // Аутентификация
  app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;

    try {
      // В реальном приложении здесь должна быть проверка пароля
      const user = await prisma.user.findUnique({
        where: { email }
      });

      if (!user) {
        return res.status(401).json({ error: 'Неверные учетные данные' });
      }

      const token = jwt.sign(
        { id: user.id, role: user.role },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
      );

      res.json({ token, user: { id: user.id, name: user.name, role: user.role } });
    } catch (error) {
      next(error);
    }
  });

  // Защищенные маршруты
  const apiRouter = express.Router();
  apiRouter.use(authenticateToken);

  // Профиль пользователя
  apiRouter.get('/profile', async (req, res) => {
    try {
      const user = await prisma.user.findUnique({
        where: { id: req.user.id },
        include: {
          contractor: true,
          clientOrders: true,
          reviews: true
        }
      });

      res.json(user);
    } catch (error) {
      next(error);
    }
  });

  // Заказы
  apiRouter.get('/orders', async (req, res) => {
    try {
      const user = await prisma.user.findUnique({
        where: { id: req.user.id }
      });

      let orders;
      if (user.role === 'CLIENT') {
        orders = await prisma.order.findMany({
          where: { clientId: user.id },
          include: {
            contractor: {
              include: { user: true }
            }
          }
        });
      } else if (user.role === 'CONTRACTOR') {
        orders = await prisma.order.findMany({
          where: {
            contractor: {
              userId: user.id
            }
          },
          include: {
            client: true
          }
        });
      } else {
        orders = await prisma.order.findMany({
          include: {
            client: true,
            contractor: {
              include: { user: true }
            }
          }
        });
      }

      res.json(orders);
    } catch (error) {
      next(error);
    }
  });

  // Создание заказа
  apiRouter.post('/orders', async (req, res) => {
    const { service, address, description } = req.body;

    try {
      const order = await prisma.order.create({
        data: {
          service,
          address,
          description,
          status: 'NEW',
          client: {
            connect: { id: req.user.id }
          }
        }
      });

      res.json(order);
    } catch (error) {
      next(error);
    }
  });

  // Обновление статуса заказа
  apiRouter.patch('/orders/:id/status', async (req, res) => {
    const { id } = req.params;
    const { status } = req.body;

    try {
      const order = await prisma.order.findUnique({
        where: { id },
        include: {
          client: true,
          contractor: {
            include: { user: true }
          }
        }
      });

      if (!order) {
        return res.status(404).json({ error: 'Заказ не найден' });
      }

      // Проверяем права на изменение статуса
      if (req.user.role !== 'ADMIN' &&
          order.clientId !== req.user.id &&
          order.contractor?.userId !== req.user.id) {
        return res.status(403).json({ error: 'Доступ запрещен' });
      }

      const updatedOrder = await prisma.order.update({
        where: { id },
        data: { status }
      });

      res.json(updatedOrder);
    } catch (error) {
      next(error);
    }
  });

  // Отзывы
  apiRouter.post('/reviews', async (req, res) => {
    const { orderId, rating, comment } = req.body;

    try {
      const order = await prisma.order.findUnique({
        where: { id: orderId },
        include: { contractor: true }
      });

      if (!order) {
        return res.status(404).json({ error: 'Заказ не найден' });
      }

      if (order.clientId !== req.user.id) {
        return res.status(403).json({ error: 'Доступ запрещен' });
      }

      const review = await prisma.review.create({
        data: {
          rating,
          comment,
          order: {
            connect: { id: orderId }
          },
          user: {
            connect: { id: req.user.id }
          }
        }
      });

      // Обновляем рейтинг подрядчика
      await prisma.contractor.update({
        where: { id: order.contractorId },
        data: {
          rating: {
            increment: rating
          },
          ratingCount: {
            increment: 1
          }
        }
      });

      res.json(review);
    } catch (error) {
      next(error);
    }
  });

  // Административные маршруты
  const adminRouter = express.Router();
  adminRouter.use(requireAdmin);

  // Статистика
  adminRouter.get('/stats', async (req, res) => {
    try {
      const [
        totalOrders,
        completedOrders,
        activeContractors,
        averageRating
      ] = await Promise.all([
        prisma.order.count(),
        prisma.order.count({
          where: { status: 'COMPLETED' }
        }),
        prisma.contractor.count({
          where: {
            user: { status: 'ACTIVE' }
          }
        }),
        prisma.contractor.aggregate({
          _avg: { rating: true }
        })
      ]);

      res.json({
        totalOrders,
        completedOrders,
        activeContractors,
        averageRating: averageRating._avg.rating || 0
      });
    } catch (error) {
      next(error);
    }
  });

  // Модерация подрядчиков
  adminRouter.patch('/contractors/:id/verify', async (req, res) => {
    const { id } = req.params;
    const { verified } = req.body;

    try {
      const contractor = await prisma.contractor.update({
        where: { id },
        data: {
          verifiedAt: verified ? new Date() : null,
          user: {
            update: {
              status: verified ? 'ACTIVE' : 'PENDING'
            }
          }
        },
        include: { user: true }
      });

      res.json(contractor);
    } catch (error) {
      next(error);
    }
  });

  // Блокировка пользователей
  adminRouter.patch('/users/:id/block', async (req, res) => {
    const { id } = req.params;
    const { blocked } = req.body;

    try {
      const user = await prisma.user.update({
        where: { id },
        data: {
          status: blocked ? 'BLOCKED' : 'ACTIVE'
        }
      });

      res.json(user);
    } catch (error) {
      next(error);
    }
  });

  // Подключаем маршруты
  app.use('/api', apiRouter);
  app.use('/api/admin', adminRouter);
}

module.exports = { setupWebRoutes }; 