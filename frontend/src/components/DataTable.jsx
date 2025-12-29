import { useState } from "react";

export default function DataTable({ columns, rows }) {
  const [sortKey, setSortKey] = useState(null);
  const [asc, setAsc] = useState(true);
  const [filter, setFilter] = useState("");

  const filtered = rows.filter(r =>
    JSON.stringify(r).toLowerCase().includes(filter.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    if (!sortKey) return 0;
    return asc
      ? String(a[sortKey]).localeCompare(String(b[sortKey]))
      : String(b[sortKey]).localeCompare(String(a[sortKey]));
  });

  return (
    <>
      <input
        placeholder="Filter…"
        className="table-filter"
        value={filter}
        onChange={e => setFilter(e.target.value)}
      />

      <table className="data-table">
        <thead>
          <tr>
            {columns.map(c => (
              <th
                key={c.key}
                onClick={() => {
                  setSortKey(c.key);
                  setAsc(sortKey === c.key ? !asc : true);
                }}
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr key={i}>
              {columns.map(c => (
                <td key={c.key}>{row[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
