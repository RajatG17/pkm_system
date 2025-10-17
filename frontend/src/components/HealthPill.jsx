import { useEffect, useState } from "react";
import { health } from "../api";

export default function HealthPill() {
    const [ok, setOK] = useState(true);
    useEffect(() => {
        let id;
        const fn = async() => setOK(await health());
        fn();
        id = setInterval(fn, 15000);
        return () => clearInterval(id);
    }, []);

    return (
        <span className={`inline-flex items-center gap-2 text-sm px-2.5 py-1 rounded ${ok ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
            <span className={`h-2 w-2 rounded-full ${ok ? "bg-green-600": "bg-red-600"}`} />
            {ok ? "Online": "Offline"}
        </span>
    );
}