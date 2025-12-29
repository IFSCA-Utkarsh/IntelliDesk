import { useEffect, useState } from "react";
import {
  getPendingEquipment,
  approveEquipment,
} from "../../services/equipment.service";

export default function EquipmentApproval() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const data = await getPendingEquipment();
    setItems(data);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return <div className="p-6 text-gray-400">Loading…</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">
        Pending Equipment Requests
      </h1>

      {items.length === 0 && (
        <p className="text-gray-500">No pending requests</p>
      )}

      <table className="w-full bg-gray-900 rounded">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-700">
            <th className="p-3">User</th>
            <th>Type</th>
            <th>Reason</th>
            <th />
          </tr>
        </thead>

        <tbody>
          {items.map((r) => (
            <tr key={r.id} className="border-b border-gray-800">
              <td className="p-3">{r.username}</td>
              <td>{r.type}</td>
              <td>{r.reason}</td>
              <td className="flex gap-2 p-3">
                <button
                  onClick={() =>
                    approveEquipment(r.id, true).then(load)
                  }
                  className="bg-green-600 px-3 py-1 rounded"
                >
                  Approve
                </button>

                <button
                  onClick={() =>
                    approveEquipment(r.id, false).then(load)
                  }
                  className="bg-red-600 px-3 py-1 rounded"
                >
                  Reject
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}