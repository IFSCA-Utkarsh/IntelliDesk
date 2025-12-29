import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { canViewPage } from "../utils/permissions";
import LogoutButton from "../components/LogoutButton";
import LogoBlock from "../components/LogoBlock";
import RoleBadge from "../components/RoleBadge";

export default function Sidebar() {
  const { role } = useAuth();

  const linkClass = ({ isActive }) =>
    `block px-4 py-2 rounded transition ${
      isActive
        ? "bg-blue-600 text-white"
        : "text-gray-300 hover:bg-gray-700 hover:text-white"
    }`;

  return (
    <aside className="w-64 h-screen bg-gray-900 text-gray-100 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-800">
        <LogoBlock />
        <div className="mt-2">
          <RoleBadge role={role} />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {canViewPage(role, "CHATBOT") && (
          <NavLink to="/chat" className={linkClass}>
            🤖 Chatbot
          </NavLink>
        )}

        {canViewPage(role, "MEETINGS") && (
          <NavLink to="/meetings" className={linkClass}>
            📅 Meetings
          </NavLink>
        )}

        {canViewPage(role, "EQUIPMENT") && (
          <NavLink to="/equipment" className={linkClass}>
            🖥 Equipment
          </NavLink>
        )}

        {canViewPage(role, "TICKETS") && (
          <NavLink to="/tickets" className={linkClass}>
            🎫 Tickets
          </NavLink>
        )}

        {/* ADMIN SECTION */}
        {canViewPage(role, "ADMIN_OVERVIEW") && (
          <>
            <div className="mt-4 mb-1 px-4 text-xs uppercase text-gray-500">
              Admin
            </div>

            <NavLink to="/admin" className={linkClass}>
              📊 Overview
            </NavLink>
          </>
        )}

        {canViewPage(role, "EQUIPMENT_APPROVAL") && (
          <NavLink to="/admin/equipment-approval" className={linkClass}>
            ✅ Equipment Approval
          </NavLink>
        )}

        {/* SUPERUSER SECTION */}
        {canViewPage(role, "AUDIT_LOGS") && (
          <>
            <div className="mt-4 mb-1 px-4 text-xs uppercase text-gray-500">
              Superuser
            </div>

            <NavLink to="/superuser/audit-logs" className={linkClass}>
              🧾 Audit Logs
            </NavLink>
          </>
        )}

        {canViewPage(role, "USER_MANAGEMENT") && (
          <NavLink to="/superuser/users" className={linkClass}>
            👥 User Management
          </NavLink>
        )}

        {canViewPage(role, "ALL_SYSTEM_DATA") && (
          <NavLink to="/superuser/all-data" className={linkClass}>
            📦 All System Data
          </NavLink>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <LogoutButton />
      </div>
    </aside>
  );
}