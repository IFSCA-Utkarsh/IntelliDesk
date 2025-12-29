import api from "./api";

/**
 * ============================
 * COMMON – USER / ADMIN / SUPERUSER
 * ============================
 */

/**
 * GET /api/equipment
 * - user      → assigned equipment
 * - admin     → all equipment
 * - superuser → all equipment
 */
export const getEquipment = async () => {
  const res = await api.get("/api/equipment");
  return res.data;
};

/**
 * ============================
 * USER ONLY
 * ============================
 */

/**
 * POST /api/equipment/request
 */
export const requestEquipment = async (payload) => {
  return api.post("/api/equipment/request", payload);
};

/**
 * POST /api/equipment/return
 */
export const returnEquipment = async (equipment_id) => {
  return api.post("/api/equipment/return", { equipment_id });
};

/**
 * ============================
 * ADMIN / SUPERUSER
 * ============================
 */

/**
 * GET /api/equipment/pending
 */
export const getPendingEquipment = async () => {
  const res = await api.get("/api/equipment/pending");
  return res.data;
};

/**
 * POST /api/equipment/approve
 * approve=true  → approve
 * approve=false → reject
 */
export const approveEquipment = async (equipment_id, approve = true) => {
  return api.post("/api/equipment/approve", {
    equipment_id,
    approve,
  });
};
