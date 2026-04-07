/**
 * lib/adventureworks.ts — Data access functions for AdventureWorks
 *
 * These functions wrap SQL queries into typed, callable functions.
 * The LLM tools in tools.ts call these to get real data.
 *
 * Schema: AdventureWorks Lite (SalesLT-style SQLite port)
 * - Product has ProductCategoryID (no subcategory table)
 * - ProductCategory uses ParentProductCategoryID for hierarchy
 * - Customer has FirstName/LastName directly (no Person table)
 */

import { query, queryOne } from "./db";

// ─── Types ────────────────────────────────────────────────────

export interface Product {
  ProductID: number;
  Name: string;
  ProductNumber: string;
  Color: string | null;
  Size: string | null;
  ListPrice: number;
  Category: string | null;
}

export interface Order {
  SalesOrderID: number;
  OrderDate: string;
  Status: number;
  TotalDue: number;
  CustomerID: number;
  ItemCount: number;
}

export interface OrderDetail {
  ProductName: string;
  OrderQty: number;
  UnitPrice: number;
  LineTotal: number;
}

export interface Customer {
  CustomerID: number;
  FirstName: string | null;
  LastName: string | null;
  CompanyName: string | null;
  EmailAddress: string | null;
}

// ─── Product Queries ──────────────────────────────────────────

export function getProductByName(name: string): Product | null {
  return queryOne<Product>(
    `SELECT
       p.ProductID, p.Name, p.ProductNumber,
       p.Color, p.Size, p.ListPrice,
       pc.Name AS Category
     FROM Product p
     LEFT JOIN ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
     WHERE p.Name LIKE ?`,
    [`%${name}%`]
  );
}

export function getProductById(id: number): Product | null {
  return queryOne<Product>(
    `SELECT
       p.ProductID, p.Name, p.ProductNumber,
       p.Color, p.Size, p.ListPrice,
       pc.Name AS Category
     FROM Product p
     LEFT JOIN ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
     WHERE p.ProductID = ?`,
    [id]
  );
}

export function searchProducts(filters: {
  category?: string;
  maxPrice?: number;
  minPrice?: number;
  color?: string;
}): Product[] {
  let sql = `
    SELECT
      p.ProductID, p.Name, p.ProductNumber,
      p.Color, p.Size, p.ListPrice,
      pc.Name AS Category
    FROM Product p
    LEFT JOIN ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
    WHERE p.ListPrice > 0`;

  const params: unknown[] = [];

  if (filters.category) {
    sql += ` AND pc.Name LIKE ?`;
    params.push(`%${filters.category}%`);
  }
  if (filters.maxPrice !== undefined) {
    sql += ` AND p.ListPrice <= ?`;
    params.push(filters.maxPrice);
  }
  if (filters.minPrice !== undefined) {
    sql += ` AND p.ListPrice >= ?`;
    params.push(filters.minPrice);
  }
  if (filters.color) {
    sql += ` AND p.Color = ?`;
    params.push(filters.color);
  }

  sql += ` ORDER BY p.ListPrice ASC LIMIT 10`;

  return query<Product>(sql, params);
}

// ─── Order Queries ────────────────────────────────────────────

export function getOrderById(orderId: number): Order | null {
  return queryOne<Order>(
    `SELECT
       h.SalesOrderID, h.OrderDate, h.Status, h.TotalDue, h.CustomerID,
       COUNT(d.SalesOrderDetailID) AS ItemCount
     FROM SalesOrderHeader h
     JOIN SalesOrderDetail d ON h.SalesOrderID = d.SalesOrderID
     WHERE h.SalesOrderID = ?
     GROUP BY h.SalesOrderID`,
    [orderId]
  );
}

export function getOrderDetails(orderId: number): OrderDetail[] {
  return query<OrderDetail>(
    `SELECT
       p.Name AS ProductName,
       d.OrderQty,
       d.UnitPrice,
       d.LineTotal
     FROM SalesOrderDetail d
     JOIN Product p ON d.ProductID = p.ProductID
     WHERE d.SalesOrderID = ?`,
    [orderId]
  );
}

export function getCustomerOrders(customerId: number): Order[] {
  return query<Order>(
    `SELECT
       h.SalesOrderID, h.OrderDate, h.Status, h.TotalDue, h.CustomerID,
       COUNT(d.SalesOrderDetailID) AS ItemCount
     FROM SalesOrderHeader h
     JOIN SalesOrderDetail d ON h.SalesOrderID = d.SalesOrderID
     WHERE h.CustomerID = ?
     GROUP BY h.SalesOrderID
     ORDER BY h.OrderDate DESC
     LIMIT 10`,
    [customerId]
  );
}

// ─── Customer Queries ─────────────────────────────────────────

export function getCustomerById(customerId: number): Customer | null {
  return queryOne<Customer>(
    `SELECT
       CustomerID,
       FirstName,
       LastName,
       CompanyName,
       EmailAddress
     FROM Customer
     WHERE CustomerID = ?`,
    [customerId]
  );
}
