import { useAuth } from "../context/AuthContext";

export default function TopBar() {
  const { user, logout } = useAuth();

  return (
    <div className="flex justify-between items-center px-6 py-3 bg-gray-900 border-b border-gray-700">
      <div className="text-lg font-semibold text-white">
        IntelliDesk
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-300">
          {user?.username} ({user?.role})
        </span>
        <button
          onClick={logout}
          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-sm rounded"
        >
          Logout
        </button>
      </div>
    </div>
  );
}