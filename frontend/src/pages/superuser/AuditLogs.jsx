import { useEffect, useState } from "react";
import { getAuditLogs } from "../../services/admin.service";
import DataTable from "../../components/DataTable";
import Spinner from "../../components/Spinner";
import ErrorBanner from "../../components/ErrorBanner";
import EmptyState from "../../components/EmptyState";

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getAuditLogs();
        setLogs(data);
      } catch {
        setError("Failed to load audit logs");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner />;
  if (error) return <ErrorBanner message={error} />;
  if (logs.length === 0)
    return <EmptyState message="No audit logs found" />;

  return (
    <section className="p-6">
      <h1 className="text-xl font-bold mb-4">Audit Logs</h1>

      <DataTable
        columns={[
          { key: "timestamp", label: "Time" },
          { key: "actor", label: "Actor" },
          { key: "action", label: "Action" },
          { key: "target", label: "Target" },
        ]}
        rows={logs}
      />
    </section>
  );
}
