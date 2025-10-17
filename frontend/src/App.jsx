import UploadBox from "./components/UploadBox";
import QABox from "./components/QABox";
import SearchBox from "./components/SearchBox";
import HealthPill from "./components/HealthPill";

  
export default function App() {
  return (
    <div className="min-h-dvh bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-6-xl px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Header */}
        <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm: justify-between">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">PKM AI</h1>
            <p className="text-sm sm:text-base text-zinc-400">Upload • Search • Ask</p>
          </div>
          <HealthPill />
        </header>

        {/* Responsive grid: 1 col on mobile, 2 on md+ */}
        <main className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-4 sm:p-5">
            <h2 className="text-lg font-semibold mb-3">Upload</h2>
            <UploadBox />
          </section>

          <section className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-4 sm:p-5">
            <h2 className="text-lg font-semibold mb-3">Search</h2>
            <SearchBox />
          </section>

          {/* QA spans full width on mobile; on md+ it also spans 2 columns */}
          <section className="md:col-span-2 rounded-2xl border border-zinc-800 bg-zinc-900/40 p-4 sm:p-5">
            <h2 className="text-lg font-semibold mb-3">Ask</h2>
            <QABox />
          </section>
        </main>
        
      </div>
    </div>
    );

}
