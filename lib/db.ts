/**
 * lib/db.ts — SQLite connection singleton
 *
 * Provides a single shared connection to the AdventureWorks database.
 * All data access functions in adventureworks.ts use this.
 *
 * ⚠️  This file is COMPLETE — no changes needed.
 */

import Database from "better-sqlite3";
import path from "path";

const DB_PATH = path.join(process.cwd(), "data", "adventureworks.db");

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true });
    _db.pragma("journal_mode = WAL");
  }
  return _db;
}

/**
 * Run a parameterized SELECT query and return all rows.
 *
 * Usage:
 *   const rows = query("SELECT * FROM Product WHERE ListPrice > ?", [1000]);
 */
export function query<T = Record<string, unknown>>(
  sql: string,
  params: unknown[] = []
): T[] {
  const db = getDb();
  const stmt = db.prepare(sql);
  return stmt.all(...params) as T[];
}

/**
 * Run a parameterized SELECT query and return the first row (or null).
 */
export function queryOne<T = Record<string, unknown>>(
  sql: string,
  params: unknown[] = []
): T | null {
  const db = getDb();
  const stmt = db.prepare(sql);
  return (stmt.get(...params) as T) ?? null;
}
