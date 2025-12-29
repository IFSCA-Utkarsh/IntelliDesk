import api from "./api";

/**
 * GET /api/admin/overview
 */
export const getAdminOverview = async () => {
  const res = await api.get("/api/admin/overview");
  return res.data;
};

/**
 * GET /api/admin/audit-log
 */
export const getAuditLogs = async () => {
  const res = await api.get("/api/admin/audit-log");
  return res.data;
};

/**
 * GET /api/admin/all-data
 */
export const getAllSystemData = async () => {
  const res = await api.get("/api/admin/all-data");
  return res.data;
};

/**
 * POST /api/admin/user/suspend
 */
export const suspendUser = async (user_id) => {
  return api.post("/api/admin/user/suspend", { user_id });
};

/**
 * POST /api/admin/user/unsuspend
 */
export const unsuspendUser = async (user_id) => {
  return api.post("/api/admin/user/unsuspend", { user_id });
};
