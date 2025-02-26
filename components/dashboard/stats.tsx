"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"

interface Stats {
  activeContractors: number
  completedOrders: number
  pendingOrders: number
  averageRating: number
}

export function DashboardStats() {
  const [stats, setStats] = useState<Stats>({
    activeContractors: 0,
    completedOrders: 0,
    pendingOrders: 0,
    averageRating: 0,
  })

  useEffect(() => {
    // In production, this would fetch from your API
    setStats({
      activeContractors: 247,
      completedOrders: 1893,
      pendingOrders: 42,
      averageRating: 4.8,
    })
  }, [])

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8 mb-8">
      <StatCard icon="engineering" value={stats.activeContractors} label="Активных Подрядчиков" color="blue" />
      <StatCard icon="assignment" value={stats.completedOrders} label="Выполненных Заказов" color="emerald" />
      <StatCard icon="pending" value={stats.pendingOrders} label="Ожидающих Заказов" color="blue" />
      <StatCard icon="stars" value={stats.averageRating} label="Средний Рейтинг" color="blue" isRating />
    </div>
  )
}

interface StatCardProps {
  icon: string
  value: number
  label: string
  color: "blue" | "emerald"
  isRating?: boolean
}

function StatCard({ icon, value, label, color, isRating }: StatCardProps) {
  const colorClasses = {
    blue: "from-gray-800/90 to-blue-900/90 border-blue-500/20 text-blue-400",
    emerald: "from-blue-900/90 to-emerald-900/90 border-emerald-500/20 text-emerald-400",
  }

  return (
    <Card
      className={`bg-gradient-to-br ${colorClasses[color]} backdrop-blur-md p-6 rounded-2xl hover:shadow-2xl hover:shadow-${color}-500/20 transition-all duration-500 transform hover:-translate-y-2 hover:scale-105 border-2 group`}
    >
      <div className="flex items-center gap-4">
        <span className="material-symbols-outlined text-3xl sm:text-4xl group-hover:rotate-180 transition-all duration-500">
          {icon}
        </span>
        <div className={`text-${color}-300`}>
          <p className="text-3xl font-black">{isRating ? value.toFixed(1) : value.toLocaleString()}</p>
          <p className="text-sm font-medium">{label}</p>
        </div>
      </div>
    </Card>
  )
}

