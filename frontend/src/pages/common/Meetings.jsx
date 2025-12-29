import { useEffect, useState } from "react";
import { getMeetings } from "../../services/meetings.service";
import DataTable from "../../components/DataTable";

export default function Meetings() {
  const [data, setData] = useState([]);

  useEffect(() => {
    getMeetings().then(setData);
  }, []);

  return (
    <section>
      <h1>Meetings</h1>

      <DataTable
        columns={[
          { key: "title", label: "Title" },
          { key: "date", label: "Date" },
          { key: "start_time", label: "Start" },
          { key: "duration", label: "Duration" },
          { key: "room", label: "Room" },
          { key: "type", label: "Type" }
        ]}
        rows={data}
      />
    </section>
  );
}
