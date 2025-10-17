import { useState } from "react";
import { fetchContext, search } from "../api";
import Modal from "./Modal";


const extOf = (p="") => (p.split(".").pop() || "").toLowerCase();

export default function SearchBox() {
  const [q, setQ] = useState("");
  const [k, setK] = useState(5);
  const [type, setType] = useState("all");
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState(null);
  const [err, setErr] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);
  const [queryForHL, setQueryForHL] = useState("");

  const openContext = async(id) => {
    // console.log("Opening context for id:", id);
    if (id !== undefined && !isNaN(Number(id))){
      try{
        const data = await fetchContext(id, 1);
      setModalData(data);
      setModalOpen(true);
      }catch(e){
        setErr(`Failed to fetch context: ${e.message}`);
      }
    }
    else{
      console.warn("Invalid document ID:", id);
      setErr("Invalid document ID");
    }
    
  }

  const HL = (t="") => {
    if (!queryForHL) return t;
    const re = new RegExp(`(${queryForHL.replace(/[.*+?^${}()|[\]\\]/g, "ig")})`);
    return t.split(re).map((part, i) => re.test(part) ? <mark key={i} className="bg-yellow-200 text-black rounded">{part}</mark>: <span key={i}>{part}</span>);
  }

  const onSearch = async() => {
    setErr("");
    setLoading(true);
    try {
      setQueryForHL(q);
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
                <span className="font-semibold underline underline-offset-2">
                  <button className="font-semibold underline ubderline-offset-2" onClick={() => openContext(r.id)} title="Open source context">
                    {r.doc_path}#{r.position}
                  </button>
                </span>
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

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={`${modalData?.doc_path}#${modalData?.position}`}>
        <div className="space-y-4">
          {modalData?.context?.map((c) => (
            <div key={c.id}>
              <div className={`text-xs text-zinc-400 mb-1 ${c.id===modalData.center ? "font-semibold" : ""}`}>
                {c.doc_path}#{c.position} {c.id===modalData.center ? "• (match)" : ""}
              </div>
              <div className="whitespace-pre-wrap text-sm text-zinc-100">{HL(c.text)}</div>
            </div>
          ))}
          <div className="pt-2">
            <button
              className="px-3 py-1 rounded bg-zinc-800"
              onClick={() => { navigator.clipboard.writeText(`${location.origin}?open=${encodeURIComponent(modalData.doc_path)}#${modalData.position}`); }}
            >
              Copy link
            </button>
          </div>
        </div>
      </Modal>
    </div>

  );

}