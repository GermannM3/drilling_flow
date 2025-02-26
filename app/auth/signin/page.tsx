"use client"

import type React from "react"

import { useState } from "react"
import { signIn } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function SignIn() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)

    try {
      const res = await signIn("credentials", {
        username: formData.get("username"),
        password: formData.get("password"),
        redirect: false,
      })

      if (res?.error) {
        setError("Invalid credentials")
        return
      }

      router.push("/dashboard")
      router.refresh()
    } catch (error) {
      setError("An error occurred")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-emerald-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-gradient-to-br from-gray-800/95 via-blue-900/90 to-emerald-900/90 backdrop-blur-md rounded-2xl shadow-[0_0_60px_rgba(0,0,0,0.5)] p-8 border-2 border-white/10">
        <h1 className="text-2xl font-bold text-center mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
          Вход в DrillFlow
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              type="text"
              name="username"
              placeholder="Имя пользователя"
              required
              className="w-full bg-gray-800/50"
            />
          </div>

          <div>
            <Input type="password" name="password" placeholder="Пароль" required className="w-full bg-gray-800/50" />
          </div>

          {error && <p className="text-red-500 text-sm text-center">{error}</p>}

          <Button type="submit" className="w-full">
            Войти
          </Button>
        </form>
      </div>
    </div>
  )
}

