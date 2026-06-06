import axios from "axios";
import { getSession, signOut } from "next-auth/react";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" }
});

api.interceptors.request.use(async (config) => {
  const session = await getSession();
  const token = (session as { access_token?: string } | null)?.access_token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) await signOut({ redirect: false });
    return Promise.reject(error);
  }
);

export default api;
