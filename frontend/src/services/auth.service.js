import api from "./api";

export async function login(username, password) {
  const res = await api.post("/auth/login", {
    username,
    password,
  });

  localStorage.setItem("token", res.data.access_token);
  localStorage.setItem("user", JSON.stringify(res.data.user));

  return res.data.user;
}

export function logout() {
  localStorage.clear();
  window.location.href = "/login";
}

export function getToken() {
  return localStorage.getItem("token");
}

export function getUser() {
  const u = localStorage.getItem("user");
  return u ? JSON.parse(u) : null;
}

export function isAuthenticated() {
  return !!getToken();
}
