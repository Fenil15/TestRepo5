export interface KPITotals {
  revenue: number;
  orders: number;
  customers: number;
  averageOrderValue: number;
}

export interface MonthlyRevenue {
  month: string;
  revenue: number;
}

export interface OrdersByCategory {
  category: string;
  orders: number;
}

export interface RecentOrder {
  id: string;
  customer: string;
  date: string;
  status: "Processing" | "Shipped" | "Delivered" | "Cancelled";
  items: number;
  total: number;
}

export const kpiTotals: KPITotals = {
  revenue: 124500,
  orders: 1840,
  customers: 976,
  averageOrderValue: 67.66,
};

export const monthlyRevenue: MonthlyRevenue[] = [
  { month: "Jan", revenue: 18200 },
  { month: "Feb", revenue: 21400 },
  { month: "Mar", revenue: 19800 },
  { month: "Apr", revenue: 23100 },
  { month: "May", revenue: 20500 },
  { month: "Jun", revenue: 21500 },
];

export const ordersByCategory: OrdersByCategory[] = [
  { category: "Electronics", orders: 420 },
  { category: "Clothing", orders: 380 },
  { category: "Home", orders: 310 },
  { category: "Sports", orders: 275 },
  { category: "Beauty", orders: 240 },
  { category: "Books", orders: 215 },
];

export const recentOrders: RecentOrder[] = [
  { id: "ORD-1048", customer: "Avery Stone", date: "2026-05-29", status: "Processing", items: 3, total: 248.5 },
  { id: "ORD-1047", customer: "Mia Chen", date: "2026-05-29", status: "Shipped", items: 1, total: 89.99 },
  { id: "ORD-1046", customer: "Noah Patel", date: "2026-05-28", status: "Delivered", items: 5, total: 421.35 },
  { id: "ORD-1045", customer: "Sofia Rivera", date: "2026-05-28", status: "Processing", items: 2, total: 134.2 },
  { id: "ORD-1044", customer: "Ethan Brooks", date: "2026-05-27", status: "Cancelled", items: 1, total: 59.0 },
  { id: "ORD-1043", customer: "Isla Morgan", date: "2026-05-27", status: "Delivered", items: 4, total: 312.75 },
];
