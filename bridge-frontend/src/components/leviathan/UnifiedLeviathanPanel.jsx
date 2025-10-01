import React, { useMemo, useState } from "react";
import { leviathanSearch } from "../../api/leviathan";

const box = {
  padding: 12,
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  background: "#fff",
};

const pill = (active) => ({
  padding: "4px 10px",
  borderRadius: 999,
  fontSize: 12,
  background: active ? "#111827" : "#e5e7eb",
  color: active ? "#fff" : "#111827",
  cursor: "pointer",
});

const tagStyle = {
  padding: "2px 8px",
  borderRadius: 999,
  fontSize: 11,
  background: "#eef2ff",
  color: "#4338ca",
  marginRight: 6,
};

function Toggle({ label, value, onChange }) {
  return (
    <label style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}

export default function UnifiedLeviathanPanel() {
  const [q, setQ] = useState("");
  const [tagsRaw, setTagsRaw] = useState(""); // comma-separated input
  const tags = useMemo(
    () =>
      tagsRaw
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    [tagsRaw]
  );

  const [planes, setPlanes] = useState({
    truth: true,
    parser: true,
    creativity: true,
  });
  const planesList = useMemo(
    () => Object.entries(planes).filter(([, v]) => v).map(([k]) => k),
    [planes]
  );

  const [limit, setLimit] = useState(25);
  const [busy, setBusy] = useState(false);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  const run = async () => {
    setBusy(true);
    setError("");
    try {
      const r = await leviathanSearch({
        query: q,
        tags: tags.length ? tags : null,
        planes: planesList.length ? planesList : null,
        limit,
      });
      setRows(r.results || []);
    } catch (e) {
      setError(e?.message || "Search failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={box}>
      <h3 style={{ margin: 0 }}>🜁 Leviathan — Unified Search</h3>
      <p style={{ marginTop: 4, color: "#6b7280" }}>
        Query <b>Truth</b>, <b>Parser</b>, and <b>Creativity</b> with tag filtering and provenance.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 140px 160px", gap: 8, marginTop: 8 }}>
        <input
          placeholder="Search query…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <input
          placeholder="tags (comma-separated)"
          value={tagsRaw}
          onChange={(e) => setTagsRaw(e.target.value)}
          title="Optional: fantasy,art,notes"
        />
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="number"
            min={1}
            max={200}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value) || 25)}
            title="Limit"
            style={{ width: 80 }}
          />
          <button onClick={run} disabled={busy || !q.trim()}>
            {busy ? "Searching…" : "Search"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 12, marginTop: 10 }}>
        <Toggle label="Truth" value={planes.truth} onChange={(v) => setPlanes((p) => ({ ...p, truth: v }))} />
        <Toggle label="Parser" value={planes.parser} onChange={(v) => setPlanes((p) => ({ ...p, parser: v }))} />
        <Toggle
          label="Creativity"
          value={planes.creativity}
          onChange={(v) => setPlanes((p) => ({ ...p, creativity: v }))}
        />
      </div>

      {error && (
        <div style={{ marginTop: 8, color: "#b91c1c" }}>
          {error}
        </div>
      )}

      <div style={{ marginTop: 12 }}>
        {rows.map((r, i) => (
          <div key={i} style={{ ...box, borderColor: "#f3f4f6", background: "#fafafa", marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <span style={pill(r.plane === "truth")}>{r.plane}</span>
              <strong>{r.title || "(untitled)"}</strong>
            </div>
            {r.tags?.length ? (
              <div style={{ marginBottom: 6 }}>
                {r.tags.map((t, idx) => (
                  <span key={idx} style={tagStyle}>{t}</span>
                ))}
              </div>
            ) : null}
            <div style={{ whiteSpace: "pre-wrap", color: "#111827" }}>{r.snippet}</div>
            <div style={{ fontSize: 12, color: "#6b7280", marginTop: 6 }}>
              {r.source ? <span>source: {r.source} • </span> : null}
              {r.path ? <span>path: {r.path} • </span> : null}
              {r.created_at ? <span>ts: {r.created_at} • </span> : null}
              {r.sha ? <span>sha: {String(r.sha).slice(0, 10)}…</span> : null}
            </div>
            {Array.isArray(r.prov) && r.prov.length > 0 && (
              <details style={{ marginTop: 6 }}>
                <summary style={{ cursor: "pointer" }}>Provenance</summary>
                <pre style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>
                  {JSON.stringify(r.prov, null, 2)}
                </pre>
              </details>
            )}
          </div>
        ))}

        {!rows.length && !busy && (
          <div style={{ color: "#6b7280", fontStyle: "italic" }}>
            No results yet. Try a query like <code>dragon</code> or <code>bridge</code>, add tags (e.g. <code>fantasy</code>), and select planes.
          </div>
        )}
      </div>
    </div>
  );
}
