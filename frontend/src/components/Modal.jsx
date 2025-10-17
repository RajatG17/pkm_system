

export default function Modal({open, onClose, title, children}) {
    if (!open) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/50" onClick={onClose}/>
            <div className="relative w-full max-w-3xl rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold">{title}</h3>
                    <button onClick={onClose} className="px-2 py-1 rounded bg-zinc-800">Close</button>
                </div>
                <div className="max-h-[70dvh] overflow-auto">{children}</div>
            </div>
        </div>
    );
}