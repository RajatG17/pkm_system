import { use, useState } from "react";
import { uploadFile, reindex } from "../api";

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
            <div className="flex items-center gap-2">
                <input type="file" onChange={(e)=>setFile(e.target.files?.[0] || null)} />
                <button onClick={doUpload} className="px-4 py-2 rounded bg-black text-white">Upload</button>
            </div>
            {msg && <div className="text-sm text-gray-700">{msg}</div>}
        </div>
    );


}