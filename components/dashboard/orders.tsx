"use client"

import { useState } from "react"
import { Drill } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Order {
  id: string
  service: string
  location: string
  status: "pending" | "assigned" | "completed"
  createdAt: string
}

export function DashboardOrders() {
  const [orders, setOrders] = useState<Order[]>([
    {
      id: "1234",
      service: "Бурение Скважины",
      location: "ул. Главная 123, Город",
      status: "pending",
      createdAt: new Date().toISOString(),
    },
    {
      id: "1235",
      service: "Ремонт Скважины",
      location: "ул. Лесная 45, Город",
      status: "pending",
      createdAt: new Date().toISOString(),
    },
    {
      id: "1236",
      service: "Бурение Канализации",
      location: "ул. Садовая 78, Город",
      status: "pending",
      createdAt: new Date().toISOString(),
    },
  ])

  const assignOrder = async (orderId: string) => {
    // In production, this would make an API call
    setOrders(orders.map((order) => (order.id === orderId ? { ...order, status: "assigned" as const } : order)))
  }

  return (
    <div className="lg:col-span-2 bg-gradient-to-br from-gray-800/90 via-blue-900/90 to-emerald-900/90 backdrop-blur-md rounded-2xl border-2 border-blue-500/20 p-6">
      <h2 className="text-2xl font-black mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
        Последние Заказы
      </h2>
      <div className="space-y-4">
        {orders.map((order) => (
          <div
            key={order.id}
            className="flex items-center justify-between p-4 hover:bg-blue-500/20 rounded-xl transition-all duration-300 group"
          >
            <div className="flex items-center gap-4">
              <Drill className="h-6 w-6 text-blue-400 group-hover:rotate-180 transition-all duration-500" />
              <div className="text-blue-300">
                <p className="font-bold text-lg">{order.service}</p>
                <p className="text-sm text-blue-400/90">{order.location}</p>
              </div>
            </div>
            <Button
              onClick={() => assignOrder(order.id)}
              disabled={order.status !== "pending"}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 border-2 border-blue-400/30 font-semibold shadow-lg hover:shadow-xl shadow-blue-500/20"
            >
              {order.status === "pending" ? "Назначить" : "Назначен"}
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}

