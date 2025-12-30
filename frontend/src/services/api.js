import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

/* ✅ REQUIRED BY MULTIPLE SERVICES */
export async function apiFetch(url, options = {}) {
  const response = await api({
    url,
    method: options.method || "GET",
    data: options.body ? JSON.parse(options.body) : undefined,
  });
  return response.data;
}

export default api;
