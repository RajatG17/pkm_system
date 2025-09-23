import { useState } from "react";
import { search } from "../api";

const extOf = (p="") => (p.split(".").pop() || "").toLowerCase();

export default function SearchBox() {
  const [q, setQ] = useState("");
  const [k, setK] = useState(5);
  const [type, setType] = useState("all");
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState(null);
  const [err, setErr] = useState("");

  const onSearch = async() => {
    setErr("");
    setLoading(true);
    try {
      const data = await search(true);
      
      const filtered = (type === "all") ? data.results:
        data.results.filter(r => {
          const ext = extOf(r.doc_path);
          const isCode = ["py", "js", "ts", "tsx", "java", "go", "rs", "cpp", "c", "h", "cs", "rb", "php", "scala", "kt", "sql"].includes(ext);
          if (type === "pdf") return ext === "pdf";
          if (type === "md") return ["md", "markdown"].includes(ext);
          if (type === "code") return isCode;
          return true;
        });
      setRes({...data, results: filtered});
    } catch(e){
      setErr(e.message);
    }finally{
      setLoading(false);
    }
  };

  const highlight = (snippet="") => {
    if (!q) return snippet;
    const re = new RegExp(`(${q.replace(/[.*+?${}()|[\]\\]/g, "\\$&")})`, "ig");
    return snippet.split(re).map((part, i) => 
      re.test(part) ? <mark key={i} className="bg-yellow-200">{part}</mark> : <span key={i}>{part}</span>
    );
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          value={q}
          onChange={e=>setQ(e.target.value)}
          placeholder="Search your corpus..."
          className="border border-zinc-700 rounded-md bg-zinc-950 px-3 py-2 flex-1"
        />
        <div className="flex gap-2">
          <select value={type} onChange={e=>setType(e.target.value)} className="border border-zinc-700 rounded-md bg-zinc-950 px-2">
            <option value="all">All</option><option value="pdf">PDFs</option>
            <option value="md">Markdown</option><option value="code">Code</option>
          </select>
          <input type="number" min="1" max="20" value={k} onChange={e=>setK(Number(e.target.value))}
                 className="border border-zinc-700 rounded-md bg-zinc-950 px-2 w-24" title="Top K"/>
          <button onClick={onSearch} disabled={loading} className="px-4 py-2 rounded-md bg-white text-black">
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {err && <div className="text-red-400 text-sm">{err}</div>}

      {res && (
        <ul className="divide-y divide-zinc-800">
          {res.results.map((r, i)=>(
            <li key={i} className="py-3">
              <div className="text-sm break-all">
                <span className="font-semibold underline underline-offset-2">{r.doc_path}#{r.position}</span>
                <span className="ml-2 text-zinc-400">score: {r.score?.toFixed?.(3)}</span>
              </div>
              {r.text_preview && (
                <div className="text-sm text-zinc-200 whitespace-pre-wrap mt-1 line-clamp-4 sm:line-clamp-none">
                  {highlight(r.text_preview.slice(0, 400))}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );

}