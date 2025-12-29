import { useEffect, useState } from "react";
import {
  getEquipment,
  requestEquipment,
  returnEquipment,
} from "../../services/equipment.service";
import { useAuth } from "../../context/AuthContext";
import Spinner from "../../components/Spinner";
import ErrorBanner from "../../components/ErrorBanner";

export default function Equipment() {
  const { user } = useAuth();
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [type, setType] = useState("");
  const [reason, setReason] = useState("");

  const loadEquipment = async () => {
    try {
      setLoading(true);
      const data = await getEquipment();
      setEquipment(data);
    } catch {
      setError("Failed to load equipment");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEquipment();
  }, []);

  async function submitRequest(e) {
    e.preventDefault();
    try {
      await requestEquipment({ type, reason });
      setType("");
      setReason("");
      loadEquipment();
    } catch {
      setError("Failed to request equipment");
    }
  }

  if (loading) return <Spinner />;
  if (error) return <ErrorBanner message={error} />;

  return (
    <section className="p-6">
      <h1 className="text-xl font-bold mb-4">My Equipment</h1>

      {/* ASSIGNED EQUIPMENT */}
      {equipment.length === 0 ? (
        <p className="text-gray-500">No equipment assigned</p>
      ) : (
        <table className="w-full bg-gray-900 rounded mb-6">
          <thead className="text-gray-400 border-b border-gray-700">
            <tr>
              <th className="p-3 text-left">Type</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {equipment.map((eq) => (
              <tr key={eq.id} className="border-b border-gray-800">
                <td className="p-3">{eq.type}</td>
                <td>{eq.status}</td>
                <td className="p-3">
                  {eq.status === "assigned" && (
                    <button
                      onClick={() =>
                        returnEquipment(eq.id).then(loadEquipment)
                      }
                      className="px-3 py-1 bg-red-600 rounded text-sm"
                    >
                      Return
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* REQUEST FORM (USER ONLY) */}
      {user.role === "user" && (
        <form onSubmit={submitRequest} className="bg-gray-900 p-4 rounded">
          <h2 className="font-semibold mb-3">Request New Equipment</h2>

          <input
            className="w-full mb-2 p-2 bg-gray-800 rounded"
            placeholder="Equipment Type (e.g. Laptop)"
            value={type}
            onChange={(e) => setType(e.target.value)}
            required
          />

          <input
            className="w-full mb-2 p-2 bg-gray-800 rounded"
            placeholder="Reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
          />

          <button className="bg-blue-600 px-4 py-2 rounded">
            Submit Request
          </button>
        </form>
      )}
    </section>
  );
}
