# AdventureWorks SQLite Database

This folder should contain `adventureworks.db`.

## How to get the database

### Option A: Download a pre-built SQLite port
Download from: https://github.com/martinandersen3d/AdventureWorks-for-SQLite

Place the `.db` file in this folder and rename it to `adventureworks.db`.

### Option B: Your instructor provides it
Your instructor may distribute the database file directly.
Place it in this folder as `adventureworks.db`.

## Expected tables

The starter kit expects these tables to exist:

| Table | Description |
|---|---|
| `Product` | Products with Name, ListPrice, Color, Size |
| `ProductCategory` | Category names (Bikes, Accessories, Clothing, Components) |
| `ProductSubcategory` | Subcategory names |
| `SalesOrderHeader` | Order headers with CustomerID, OrderDate, TotalDue, Status |
| `SalesOrderDetail` | Order line items with ProductID, OrderQty, UnitPrice |
| `Customer` | Customers with PersonID, TerritoryID |
| `Person` | Person names (FirstName, LastName) |

## Verify your database

```bash
sqlite3 data/adventureworks.db "SELECT Name, ListPrice FROM Product WHERE Name LIKE '%Mountain-200%' LIMIT 3;"
```

Expected: Mountain-200 variants with ListPrice around $2,294.99.
