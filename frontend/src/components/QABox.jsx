import { useState } from "react";
import { fetchContext,qa } from "../api";
import Modal from "./Modal";

export default function QABox(){
    const [q, setQ] = useState("");
    const [k, setK] = useState(2);
    const [maxCtx, setMaxCtx] = useState(1800);
    const [loading, setLoading] = useState(false);
    const [res, setRes] = useState(null);
    const [err, setErr] = useState("");
    const [modalOpen, setModalOpen] = useState(false);
    const [modalData, setModalData] = useState(null);
    const [queryForHL, setQueryForHL] = useState("");
    
    const openContext = async(id) => {
        console.log("Opening context for id:", id);
        if (id !== undefined && !isNaN(Number(id))){
            try{
              const data = await fetchContext(id, 1);
            setModalData(data);
            setModalOpen(true);
            }catch(e){
              setErr(`Failed to fetch context: ${e.message}`);
            }
        }else{
            console.warn("Invalid document ID:", id);
            setErr(`Invalid document ID ${id}`);
        }
    }

    const HL = (t="") => {
        if (!queryForHL) return t;
        const re = new RegExp(`(${queryForHL.replace(/[.*+?^${}()|[\]\\]/g, "ig")})`);
        return t.split(re).map((part, i) => re.test(part) ? <mark key={i} className="bg-yellow-200 text-black rounded">{part}</mark>: <span key={i}>{part}</span>);
    }

    const ask = async () => {
        setErr("");
        setLoading(true);
        try {
            setQueryForHL(q);
            const data = await qa(q, k, maxCtx);
            setRes(data);
        } catch (e) {
            setErr(e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-2">
                <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask a question..."
                    className="border border-zinc-700 rounded-md bg-zinc-950 px-3 py-2 flex-1"/>
                <div className="flex gap-2">
                <input type="number" min="1" max="10" value={k} onChange={e=>setK(Number(e.target.value))}
                        className="border border-zinc-700 rounded-md bg-zinc-950 px-2 w-20" title="Top K"/>
                <input type="number" min="600" max="6000" step="200" value={maxCtx} onChange={e=>setMaxCtx(Number(e.target.value))}
                        className="border border-zinc-700 rounded-md bg-zinc-950 px-2 w-28" title="Max context chars"/>
                <button onClick={ask} disabled={loading} className="px-4 py-2 rounded-md bg-white text-black">
                    {loading ? "Thinking..." : "Ask"}
                </button>
                </div>
            </div>

            {err && <div className="text-red-400 text-sm">{err}</div>}

            {res && (
                <div className="space-y-2">
                <div className="font-semibold">Answer</div>
                <div className="whitespace-pre-wrap text-zinc-200">{res.answer}</div>
                <div className="font-semibold pt-2">Sources</div>
                <ul className="list-disc pl-5 space-y-2">
                    {res.sources?.map((s, i)=>(
                    <li key={i} className="break-all">
                        <code className="text-xs sm:text-sm">
                            <button className="font-semibold underline underline-offset-2" 
                                onClick={() => openContext(s.id, 1)} title="Open source location" >
                                    {s.doc_path}#{s.position}
                            </button>
                        </code>
                        <span className="text-zinc-400"> · score {s.score?.toFixed?.(3)}</span>
                        <div className="text-sm text-zinc-200 mt-1">{s.preview}</div>
                    </li>
                    ))}
                </ul>
                </div>
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