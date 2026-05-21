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
