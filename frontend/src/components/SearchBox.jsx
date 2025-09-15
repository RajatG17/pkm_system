import { useState } from "react";
import { search } from "../api";

export default function SearchBox() {
  const [q, setQ] = useState("");
  const [k, setK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState(null);
  const [err, setErr] = useState("");

  const onSearch = async () => {
    setErr(""); setLoading(true);
    try {
      const data = await search(q, k);
      setRes(data);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          value={q}
          onChange={e=>setQ(e.target.value)}
          placeholder="Search your corpus..."
          className="border rounded px-3 py-2 flex-1"
        />
        <input
          type="number"
          min="1"
          max="20"
          value={k}
          onChange={e=>setK(Number(e.target.value))}
          className="border rounded px-2 w-20"
          title="Top K"
        />
        <button onClick={onSearch} disabled={loading} className="px-4 py-2 rounded bg-black text-white">
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
      {err && <div className="text-red-600 text-sm">{err}</div>}
      {res && (
        <div className="space-y-2">
          <div className="text-sm text-gray-500">Query: <code>{res.query}</code></div>
          <ul className="divide-y">
            {res.results.map((r, i)=>(
              <li key={i} className="py-2">
                <div className="text-sm">
                  <span className="font-semibold">{r.doc_path}#{r.position}</span>
                  <span className="ml-2 text-gray-500">score: {r.score.toFixed(3)}</span>
                </div>
                {"text_preview" in r && (
                  <div className="text-sm text-gray-700 whitespace-pre-wrap mt-1">
                    {r.text_preview?.slice?.(0, 240)}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
