import { Telegraf } from "telegraf"
import { db } from "./db"

const bot = new Telegraf(process.env.TELEGRAM_TOKEN!)

bot.command("start", async (ctx) => {
  await ctx.reply("Добро пожаловать в DrillFlow! Выберите вашу роль:", {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "Я заказчик", callback_data: "role:client" },
          { text: "Я подрядчик", callback_data: "role:contractor" },
        ],
      ],
    },
  })
})

bot.action(/role:(.+)/, async (ctx) => {
  const role = ctx.match[1]
  const userId = ctx.from?.id

  if (!userId) {
    return ctx.reply("Ошибка идентификации пользователя")
  }

  await db.query(
    "INSERT INTO users (telegram_id, role) VALUES ($1, $2) ON CONFLICT (telegram_id) DO UPDATE SET role = $2",
    [userId, role],
  )

  const message =
    role === "client"
      ? "Отлично! Теперь вы можете создать заказ на бурение."
      : "Отлично! Пожалуйста, заполните информацию о вашей компании."

  await ctx.reply(message)
})

// Start bot
bot.launch().catch(console.error)

// Enable graceful stop
process.once("SIGINT", () => bot.stop("SIGINT"))
process.once("SIGTERM", () => bot.stop("SIGTERM"))

export { bot }

