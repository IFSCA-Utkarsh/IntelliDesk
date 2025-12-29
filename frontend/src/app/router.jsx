import { createBrowserRouter } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import RequireRole from "../components/RequireRole";
import MainLayout from "../layout/MainLayout";
import { ROLES } from "../constants/roles";

import Login from "../pages/Login";
import NotFound from "../pages/NotFound";

import Chatbot from "../pages/common/Chatbot";
import Meetings from "../pages/common/Meetings";
import Equipment from "../pages/common/Equipment";
import Tickets from "../pages/common/Tickets";

import AdminOverview from "../pages/admin/AdminOverview";
import EquipmentApproval from "../pages/admin/EquipmentApproval";

import AuditLogs from "../pages/superuser/AuditLogs";
import UserManagement from "../pages/superuser/UserManagement";
import AllSystemData from "../pages/superuser/AllSystemData";

export default createBrowserRouter([
  { path: "/login", element: <Login /> },

  {
    path: "/",
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      { path: "chat", element: <Chatbot /> },
      { path: "meetings", element: <Meetings /> },
      { path: "equipment", element: <Equipment /> },
      { path: "tickets", element: <Tickets /> },

      {
        path: "admin",
        element: (
          <RequireRole allowed={[ROLES.ADMIN, ROLES.SUPERUSER]}>
            <AdminOverview />
          </RequireRole>
        ),
      },
      {
        path: "admin/equipment",
        element: (
          <RequireRole allowed={[ROLES.ADMIN, ROLES.SUPERUSER]}>
            <EquipmentApproval />
          </RequireRole>
        ),
      },

      {
        path: "superuser/audit-logs",
        element: (
          <RequireRole allowed={[ROLES.SUPERUSER]}>
            <AuditLogs />
          </RequireRole>
        ),
      },
      {
        path: "superuser/users",
        element: (
          <RequireRole allowed={[ROLES.SUPERUSER]}>
            <UserManagement />
          </RequireRole>
        ),
      },
      {
        path: "superuser/all-data",
        element: (
          <RequireRole allowed={[ROLES.SUPERUSER]}>
            <AllSystemData />
          </RequireRole>
        ),
      },

      { path: "*", element: <NotFound /> },
    ],
  },
]);
