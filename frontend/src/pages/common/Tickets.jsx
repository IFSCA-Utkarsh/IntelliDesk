import { useEffect, useState } from "react";
import {
  getTickets,
  closeTicket,
  escalateTicket,
} from "../../services/tickets.service";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../constants/roles";
import Spinner from "../../components/Spinner";
import ErrorBanner from "../../components/ErrorBanner";
import EmptyState from "../../components/EmptyState";

export default function Tickets() {
  const { user } = useAuth();

  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const data = await getTickets();
      setTickets(data);
    } catch {
      setError("Failed to load tickets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  if (loading) return <Spinner />;
  if (error) return <ErrorBanner message={error} />;
  if (tickets.length === 0)
    return <EmptyState message="No tickets found" />;

  const canClose =
    user.role === ROLES.ADMIN || user.role === ROLES.SUPERUSER;

  const canEscalate = user.role === ROLES.SUPERUSER;

  return (
    <section className="p-6">
      <h1 className="text-xl font-bold mb-4">🎫 Tickets</h1>

      <table className="w-full bg-gray-900 rounded-lg overflow-hidden">
        <thead className="bg-gray-800 text-gray-400 text-sm">
          <tr>
            <th className="p-3 text-left">Title</th>
            <th>Status</th>
            <th>Created By</th>
            <th>Assigned To</th>
            <th />
          </tr>
        </thead>

        <tbody>
          {tickets.map((t) => (
            <tr
              key={t.id}
              className="border-t border-gray-800 hover:bg-gray-800/50"
            >
              <td className="p-3">{t.title}</td>

              <td>
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    t.status === "open"
                      ? "bg-yellow-600"
                      : t.status === "in_progress"
                      ? "bg-blue-600"
                      : "bg-green-600"
                  }`}
                >
                  {t.status}
                </span>
              </td>

              <td>{t.created_by_username}</td>
              <td>{t.assigned_to || "-"}</td>

              <td className="p-2 flex gap-2">
                {/* ADMIN + SUPERUSER */}
                {canClose && t.status !== "closed" && (
                  <button
                    onClick={() =>
                      closeTicket(t.id).then(loadTickets)
                    }
                    className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
                  >
                    Close
                  </button>
                )}

                {/* SUPERUSER ONLY */}
                {canEscalate && t.status !== "closed" && (
                  <button
                    onClick={() =>
                      escalateTicket(t.id).then(loadTickets)
                    }
                    className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                  >
                    Escalate
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}