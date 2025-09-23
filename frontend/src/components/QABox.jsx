import { useState } from "react";
import { qa } from "../api";

export default function QABox(){
    const [q, setQ] = useState("");
    const [k, setK] = useState(5);
    const [maxCtx, setMaxCtx] = useState(1800);
    const [loading, setLoading] = useState(false);
    const [res, setRes] = useState(null);
    const [err, setErr] = useState("");

    const ask = async () => {
        setErr("");
        setLoading(true);
        try {
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
                        <code className="text-xs sm:text-sm">{s.doc_path}#{s.position}</code>
                        <span className="text-zinc-400"> · score {s.score?.toFixed?.(3)}</span>
                        <div className="text-sm text-zinc-200 mt-1">{s.preview}</div>
                    </li>
                    ))}
                </ul>
                </div>
            )}
        </div>
    );
}