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
            <div className="flex gap-2">
                <input
                    value={q}
                    onChange={e=>setQ(e.target.value)}
                    placeholder="Ask a question..."
                    className="border rounded px-3 py-2 flex-1" />
                <input type="number" min="1" max="10" value={k} onChange={e=>setK(Number(e.target.value))} className="border rounded px-2 w-20" title="Top K"/>
                <input type="number" min="600" max="6000" step="200" value={maxCtx} onChange={e=>setMaxCtx(Number(e.target.value))} className="border rounded px-2 w-28" title="Max context chars"/>
                <button onClick={ask} disabled={loading} className="px-4 py-2 rounded bg-black text-white">
                    {loading ? "Thinking..." : "Ask"}
                </button>
            </div>
            {err && <div className="text-red-600 text-sm">{err}</div>}
            {res && (
                <div className="space-y-2">
                    <div className="font-semibold">Answer</div>
                    <div className="whitespace-pre-wrap">{res.answer}</div>
                    <div className="font-semibold pt-2">Sources</div>
                    <ul className="list-disc pl-5">
                        {res.sources?.map((s,i)=>(
                            <li key={i}>
                                <code>{s.doc_path}#{s.position}</code> <span className="text-gray-500">score {s.score?.toFixed?.(3)}</span>
                                <div className="text-sm text-gray-700">{s.preview}</div>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}