import { useEffect, useState } from "react";
import { getAdminOverview } from "../../services/admin.service";

export default function AdminOverview() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getAdminOverview().then(setData);
  }, []);

  if (!data) return null;

  const Card = ({ label, value }) => (
    <div className="bg-gray-900 p-5 rounded shadow">
      <div className="text-gray-400 text-sm">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );

  return (
    <div className="p-6 grid grid-cols-4 gap-4">
      <Card label="Total Users" value={data.users} />
      <Card label="Open Tickets" value={data.open_tickets} />
      <Card label="Pending Equipment" value={data.pending_equipment} />
      <Card label="Meetings Today" value={data.meetings_today} />
    </div>
  );
}
