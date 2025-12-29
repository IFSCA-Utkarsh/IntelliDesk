import { ROLES } from "../constants/roles";

export const PAGE_PERMISSIONS = {
  CHATBOT: [ROLES.USER, ROLES.ADMIN, ROLES.SUPERUSER],
  MEETINGS: [ROLES.USER, ROLES.ADMIN, ROLES.SUPERUSER],
  EQUIPMENT: [ROLES.USER, ROLES.ADMIN, ROLES.SUPERUSER],
  TICKETS: [ROLES.USER, ROLES.ADMIN, ROLES.SUPERUSER],

  ADMIN_OVERVIEW: [ROLES.ADMIN, ROLES.SUPERUSER],
  EQUIPMENT_APPROVAL: [ROLES.ADMIN, ROLES.SUPERUSER],

  // ✅ ADD THIS
  AUDIT_LOGS: [ROLES.SUPERUSER],
  USER_MANAGEMENT: [ROLES.SUPERUSER],
  ALL_SYSTEM_DATA: [ROLES.SUPERUSER],
};

export function hasPermission(role, allowedRoles) {
  if (!role) return false;
  return allowedRoles.includes(role);
}

export function canViewPage(role, pageKey) {
  const allowed = PAGE_PERMISSIONS[pageKey];
  if (!allowed) return false;
  return allowed.includes(role);
}
