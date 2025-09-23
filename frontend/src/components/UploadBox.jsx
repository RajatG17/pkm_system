import { useState } from "react";
import { uploadFile, reindex, incremental } from "../api";

export default function UploadBox() {
    const [file, setFile] = useState(null);
    const [msg, setMsg] = useState("");

    const doUpload = async() => {
        if (!file) return setMsg("Pick a file first.");
        setMsg("Uploading..");
        try {
            await uploadFile(file);
            setMsg("Uploaded. Reindexing...");
            await reindex();
            setMsg("Reindexed successfully");
        }catch (e){
            setMsg("Error " + e.message);
        }
        
    };


    return (
        <div className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-2">
                <input
                type="file"
                onChange={(e)=>setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm file:mr-3 file:px-3 file:py-2 file:rounded-md
                            file:border-0 file:bg-zinc-800 file:text-zinc-100 file:cursor-pointer"
                />
                <div className="flex gap-2">
                <button onClick={doUpload} className="px-4 py-2 rounded-md bg-white text-black w-full sm:w-auto">
                    Upload & Reindex
                </button>
                <button
                    onClick={async () => { setMsg("Incremental reindex..."); try { await incremental(); setMsg("Incremental done."); } catch(e){ setMsg("Error: " + e.message);} }}
                    className="px-3 py-2 rounded-md border border-zinc-700 w-full sm:w-auto"
                    title="Scan for new/changed/deleted files"
                >
                    Reindex All (Incremental)
                </button>
                </div>
            </div>
            {msg && <div className="text-sm text-zinc-300">{msg}</div>}
        </div>
    );


}