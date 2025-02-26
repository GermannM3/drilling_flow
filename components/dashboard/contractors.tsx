"use client"

import { useState } from "react"
import { Star, User } from "lucide-react"

interface Contractor {
  id: string
  name: string
  rating: number
  completedOrders: number
  status: "active" | "busy" | "offline"
}

export function DashboardContractors() {
  const [contractors, setContractors] = useState<Contractor[]>([
    {
      id: "1",
      name: "Иван Иванов",
      rating: 4.9,
      completedOrders: 156,
      status: "active",
    },
    {
      id: "2",
      name: "Петр Петров",
      rating: 4.8,
      completedOrders: 143,
      status: "active",
    },
    {
      id: "3",
      name: "Сергей Сергеев",
      rating: 4.7,
      completedOrders: 128,
      status: "busy",
    },
  ])

  return (
    <div className="bg-gradient-to-br from-emerald-900/90 via-blue-900/90 to-gray-800/90 backdrop-blur-md rounded-2xl border-2 border-emerald-500/20 p-6">
      <h2 className="text-2xl font-black mb-6 text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-400">
        Лучшие Подрядчики
      </h2>
      <div className="space-y-4">
        {contractors.map((contractor) => (
          <div
            key={contractor.id}
            className="flex items-center justify-between p-4 hover:bg-blue-500/20 rounded-xl transition-all duration-300 group"
          >
            <div className="flex items-center gap-3">
              <User className="h-6 w-6 text-blue-400 group-hover:rotate-180 transition-all duration-500" />
              <div>
                <p className="font-bold text-lg text-blue-300">{contractor.name}</p>
                <p className="text-sm text-blue-400/90">{contractor.completedOrders} заказов</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-blue-300">
              <Star className="h-5 w-5 text-yellow-500 fill-yellow-500 animate-pulse" />
              <span className="font-bold">{contractor.rating}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

