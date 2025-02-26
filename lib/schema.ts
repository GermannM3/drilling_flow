import { pgTable, serial, varchar, timestamp, decimal, integer } from "drizzle-orm/pg-core"

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  telegramId: varchar("telegram_id", { length: 256 }).unique().notNull(),
  role: varchar("role", { length: 20 }).notNull(),
  createdAt: timestamp("created_at").defaultNow(),
})

export const contractors = pgTable("contractors", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  name: varchar("name", { length: 255 }).notNull(),
  specialization: varchar("specialization", { length: 50 }).array(),
  workRadius: integer("work_radius"),
  rating: decimal("rating", { precision: 3, scale: 2 }).default("5.00"),
  status: varchar("status", { length: 20 }).default("pending"),
  createdAt: timestamp("created_at").defaultNow(),
})

export const orders = pgTable("orders", {
  id: serial("id").primaryKey(),
  clientId: integer("client_id").references(() => users.id),
  contractorId: integer("contractor_id").references(() => contractors.id),
  serviceType: varchar("service_type", { length: 50 }).notNull(),
  status: varchar("status", { length: 20 }).default("pending"),
  rating: integer("rating"),
  createdAt: timestamp("created_at").defaultNow(),
  completedAt: timestamp("completed_at"),
})

