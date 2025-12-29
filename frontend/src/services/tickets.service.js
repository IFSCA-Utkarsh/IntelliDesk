import api from "./api";

/**
 * GET /api/tickets
 */
export const getTickets = async () => {
  const res = await api.get("/api/tickets");
  return res.data;
};

/**
 * POST /api/tickets
 */
export const createTicket = async (payload) => {
  return api.post("/api/tickets", payload);
};

/**
 * POST /api/tickets/close
 */
export const closeTicket = async (ticket_id) => {
  return api.post("/api/tickets/close", { ticket_id });
};

/**
 * POST /api/tickets/escalate
 */
export const escalateTicket = async (ticket_id) => {
  return api.post("/api/tickets/escalate", { ticket_id });
};
