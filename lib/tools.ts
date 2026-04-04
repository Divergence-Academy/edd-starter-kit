/**
 * lib/tools.ts — Tool definitions and executor for LLM tool calling
 *
 * Each tool wraps an AdventureWorks data access function.
 * The LLM sees the tool definitions (name + description + parameters)
 * and decides when to call them. The executor runs the actual function.
 *
 * ⚠️  This file is COMPLETE — no changes needed.
 */

import {
  getProductByName,
  getProductById,
  searchProducts,
  getOrderById,
  getOrderDetails,
  getCustomerOrders,
  getCustomerById,
} from "./adventureworks";

// ─── Tool Definitions (OpenAI function calling format) ────────

export const TOOL_DEFINITIONS = [
  {
    type: "function" as const,
    function: {
      name: "lookup_product",
      description:
        "Look up a product by name. Returns price, color, size, and category. Use this when a customer asks about a specific product.",
      parameters: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description: "Full or partial product name, e.g. 'Mountain-200'",
          },
        },
        required: ["name"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "search_products",
      description:
        "Search for products by category, price range, or color. Use this when a customer wants recommendations or is browsing.",
      parameters: {
        type: "object",
        properties: {
          category: {
            type: "string",
            description: "Product category like 'Bikes', 'Accessories', 'Clothing'",
          },
          maxPrice: {
            type: "number",
            description: "Maximum price in dollars",
          },
          minPrice: {
            type: "number",
            description: "Minimum price in dollars",
          },
          color: {
            type: "string",
            description: "Product color",
          },
        },
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "lookup_order",
      description:
        "Look up an order by order ID. Returns order status, total, and line items. Use this when a customer asks about a specific order.",
      parameters: {
        type: "object",
        properties: {
          orderId: {
            type: "number",
            description: "The sales order ID number, e.g. 43659",
          },
        },
        required: ["orderId"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_customer_orders",
      description:
        "Get recent orders for a customer by their customer ID. Use when a customer wants to see their order history.",
      parameters: {
        type: "object",
        properties: {
          customerId: {
            type: "number",
            description: "The customer ID number",
          },
        },
        required: ["customerId"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "lookup_customer",
      description:
        "Look up customer information by customer ID. Returns name and territory.",
      parameters: {
        type: "object",
        properties: {
          customerId: {
            type: "number",
            description: "The customer ID number",
          },
        },
        required: ["customerId"],
      },
    },
  },
];

// ─── Tool Executor ────────────────────────────────────────────

export interface ToolResult {
  toolName: string;
  args: Record<string, unknown>;
  result: unknown;
}

/**
 * Execute a tool by name with the given arguments.
 * Returns the result as a JSON-serializable object.
 */
export function executeTool(
  name: string,
  args: Record<string, unknown>
): unknown {
  switch (name) {
    case "lookup_product": {
      const product = getProductByName(args.name as string);
      if (!product) return { error: `No product found matching "${args.name}"` };
      return product;
    }

    case "search_products": {
      const results = searchProducts({
        category: args.category as string | undefined,
        maxPrice: args.maxPrice as number | undefined,
        minPrice: args.minPrice as number | undefined,
        color: args.color as string | undefined,
      });
      if (results.length === 0) return { error: "No products match your criteria" };
      return { count: results.length, products: results };
    }

    case "lookup_order": {
      const order = getOrderById(args.orderId as number);
      if (!order) return { error: `No order found with ID ${args.orderId}` };
      const details = getOrderDetails(args.orderId as number);
      return { order, lineItems: details };
    }

    case "get_customer_orders": {
      const orders = getCustomerOrders(args.customerId as number);
      if (orders.length === 0)
        return { error: `No orders found for customer ${args.customerId}` };
      return { count: orders.length, orders };
    }

    case "lookup_customer": {
      const customer = getCustomerById(args.customerId as number);
      if (!customer)
        return { error: `No customer found with ID ${args.customerId}` };
      return customer;
    }

    default:
      return { error: `Unknown tool: ${name}` };
  }
}
