import { NextResponse } from "next/server"
import { sql } from "@vercel/postgres"
import { redis } from "@/lib/redis"

export async function GET() {
  try {
    // Try to get stats from cache first
    const cachedStats = await redis.get("dashboard:stats")
    if (cachedStats) {
      return NextResponse.json(JSON.parse(cachedStats))
    }

    // If not in cache, get from database
    const stats = await Promise.all([
      sql`SELECT COUNT(*) FROM contractors WHERE status = 'active'`,
      sql`SELECT COUNT(*) FROM orders WHERE status = 'completed'`,
      sql`SELECT COUNT(*) FROM orders WHERE status = 'pending'`,
      sql`SELECT AVG(rating) FROM orders WHERE status = 'completed'`,
    ]).then(([activeContractors, completedOrders, pendingOrders, avgRating]) => ({
      activeContractors: Number(activeContractors.rows[0].count) || 0,
      completedOrders: Number(completedOrders.rows[0].count) || 0,
      pendingOrders: Number(pendingOrders.rows[0].count) || 0,
      averageRating: Number(avgRating.rows[0].avg) || 0,
    }))

    // Cache the results
    await redis.setex("dashboard:stats", 300, JSON.stringify(stats))

    return NextResponse.json(stats)
  } catch (error) {
    console.error("Error fetching stats:", error)
    return NextResponse.json({ error: "Failed to fetch stats" }, { status: 500 })
  }
}

