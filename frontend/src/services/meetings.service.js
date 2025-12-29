import api from "./api";

/**
 * GET /api/meetings
 */
export const getMeetings = async () => {
  const res = await api.get("/api/meetings");
  return res.data;
};

/**
 * POST /api/meetings
 */
export const createMeeting = async (payload) => {
  return api.post("/api/meetings", payload);
};
