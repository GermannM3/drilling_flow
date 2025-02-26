"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { Bell, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export function DashboardHeader() {
  const { data: session } = useSession()
  const [notifications] = useState([
    {
      id: 1,
      title: "Новый Заказ #1234",
      description: "Запрос на бурение скважины - 5км",
    },
  ])

  return (
    <header className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
      <div className="flex items-center gap-4 group">
        <span className="material-symbols-outlined text-4xl sm:text-5xl text-blue-400 transform group-hover:rotate-180 transition-all duration-500 shadow-lg shadow-blue-500/50">
          water_drop
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
          Панель Управления DrillFlow
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5 text-blue-400" />
              {notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-bounce shadow-lg shadow-red-500/50">
                  {notifications.length}
                </span>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-72">
            {notifications.map((notification) => (
              <DropdownMenuItem key={notification.id} className="p-3">
                <div className="flex flex-col gap-1">
                  <p className="font-bold">{notification.title}</p>
                  <p className="text-sm text-muted-foreground">{notification.description}</p>
                </div>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2">
              <User className="h-5 w-5" />
              <span className="font-semibold">{session?.user?.name || "Администратор"}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Профиль</DropdownMenuItem>
            <DropdownMenuItem>Настройки</DropdownMenuItem>
            <DropdownMenuItem>Выйти</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}

