// Обработчик для вебхука Telegram на Vercel

export default function handler(req, res) {
  if (req.method === 'GET') {
    // Обработка GET-запроса (для проверки вебхука)
    const response = {
      app: "DrillFlow Bot",
      version: "1.0.0",
      status: "running",
      webhook_url: "https://drilling-flow.vercel.app/api/tg_webhook",
      telegram_bot: "@Drill_Flow_bot",
      updated_at: new Date().toISOString(),
      version_tag: "v2023-10-21-01",
      env: process.env.VERCEL_ENV || "unknown"
    };
    
    res.status(200).json(response);
  } else if (req.method === 'POST') {
    // Обработка POST-запроса от Telegram
    console.log('Received webhook data:', req.body);
    
    // Здесь должен быть код обработки сообщений от Telegram
    // В качестве примера мы просто логируем и возвращаем успех
    
    res.status(200).send('OK');
  } else {
    // Метод не поддерживается
    res.status(405).send('Method Not Allowed');
  }
} 