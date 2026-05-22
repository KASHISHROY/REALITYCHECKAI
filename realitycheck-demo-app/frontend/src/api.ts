import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const ANALYTICS_KEY = import.meta.env.VITE_ANALYTICS_KEY;

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "X-Analytics-Key": ANALYTICS_KEY,
  },
});

export async function loadDashboard() {
  const users = await fetch("/api/users");
  const login = await fetch("/api/login", { method: "POST" });
  const products = await api.get("/api/products");
  const orders = await api.post("/api/orders", { sku: "reality-widget" });
  const reports = await api.get("/api/reports");
  const deleteUser = await api.delete("/api/users/123");
  const profile = await fetch("/api/profile", { method: "PATCH" });
  const admin = await fetch("/api/v2/admin");

  return {
    users,
    login,
    products,
    orders,
    reports,
    deleteUser,
    profile,
    admin,
  };
}
