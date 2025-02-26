import { sql } from "@vercel/postgres"
import { drizzle } from "drizzle-orm/vercel-postgres"

// Export the raw sql client for direct queries
export { sql }

// Export the drizzle client for typed queries
export const db = drizzle(sql)

