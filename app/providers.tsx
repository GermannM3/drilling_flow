"use client"

import type React from "react"

import { ThemeProvider } from "next-themes"
import { SessionProvider } from "next-auth/react"

export function Providers({
  children,
  session,
}: {
  children: React.ReactNode
  session?: any
}) {
  return (
    <SessionProvider session={session}>
      <ThemeProvider attribute="class" defaultTheme="dark">
        {children}
      </ThemeProvider>
    </SessionProvider>
  )
}

