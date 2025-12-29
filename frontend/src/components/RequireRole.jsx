import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "./Spinner";

export default function RequireRole({ allowed, children }) {
  const { role, loading } = useAuth();

  if (loading) return <Spinner />;
  if (!role) return <Navigate to="/login" replace />;
  if (!allowed.includes(role)) return <Navigate to="/not-found" replace />;

  return children;
}
