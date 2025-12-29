import { useEffect, useState } from "react";
import { getAllSystemData } from "../../services/admin.service";
import { downloadCSV } from "../../utils/csv";

export default function AllSystemData() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getAllSystemData().then(setData);
  }, []);

  if (!data) return <p>Loading…</p>;

  return (
    <section>
      <h1>All System Data</h1>

      <button onClick={() => downloadCSV("users.csv", data.users)}>
        Export Users CSV
      </button>

      <button onClick={() => downloadCSV("meetings.csv", data.meetings)}>
        Export Meetings CSV
      </button>

      <button onClick={() => downloadCSV("tickets.csv", data.tickets)}>
        Export Tickets CSV
      </button>

      <button onClick={() => downloadCSV("equipment.csv", data.equipment)}>
        Export Equipment CSV
      </button>
    </section>
  );
}
