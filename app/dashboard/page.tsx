import { DashboardHeader } from "@/components/dashboard/header"
import { DashboardStats } from "@/components/dashboard/stats"
import { DashboardOrders } from "@/components/dashboard/orders"
import { DashboardContractors } from "@/components/dashboard/contractors"

export default async function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-emerald-900 flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-[1200px] bg-gradient-to-br from-gray-800/95 via-blue-900/90 to-emerald-900/90 backdrop-blur-md rounded-2xl shadow-[0_0_60px_rgba(0,0,0,0.5)] p-4 sm:p-8 border-2 sm:border-4 border-white/10">
        <DashboardHeader />
        <DashboardStats />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          <DashboardOrders />
          <DashboardContractors />
        </div>
      </div>
    </div>
  )
}

