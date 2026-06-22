import axios, { isAxiosError } from "axios";

const normalizeApiBaseUrl = (url: string) =>
  url.trim().replace(/\/+$/, "").replace(/\/v1$/, "");

export const API_BASE_URL = normalizeApiBaseUrl(
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"
);

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

type AuthResponse = {
  message: string;
};

type RegisterPayload = {
  companyName: string;
  email: string;
  password: string;
};

type LoginPayload = {
  email: string;
  password: string;
};

type ApiErrorPayload = {
  detail?: string;
  message?: string;
};

const postAuthForm = async <TResponse>(path: string, formData: FormData) => {
  const response = await api.post<TResponse>(path, formData); 
  return response;
};

export const loginRecruiter = ({ email, password }: LoginPayload) => {
  const formData = new FormData();
  formData.append("email", email);
  formData.append("password", password);
  return postAuthForm<AuthResponse>("/v1/login", formData); 
};

export const registerRecruiter = ({ companyName, email, password }: RegisterPayload) => {
  const formData = new FormData();
  formData.append("company_name", companyName);
  formData.append("email", email);
  formData.append("password", password);

  return postAuthForm<AuthResponse>("/v1/register", formData);
};

export const getApiErrorMessage = (error: unknown, fallback: string) => {
  if (isAxiosError<ApiErrorPayload>(error)) {
    const detail = error.response?.data?.detail;

    // FastAPI 422 returns detail as an array of validation error objects
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg ?? "Validation error").join(", ");
    }

    if (detail || error.response?.data?.message) {
      return detail ?? error.response?.data?.message ?? fallback;
    }

    if (!error.response) {
      return `${fallback} Tried ${API_BASE_URL}.`;
    }

    return error.message;
  }

  return error instanceof Error ? error.message : fallback;
};

export default api;
