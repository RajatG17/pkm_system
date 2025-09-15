import { useState } from "react";
import UploadBox from "./components/UploadBox";
import QABox from "./components/QABox";
import SearchBox from "./components/SearchBox";
  
export default function App() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold">PKM Assistant</h1>
        <p className="text-gray-600">Upload - Search - Ask</p>
      </header>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Upload</h2>
        <UploadBox />
      </section>

      <section className="space-y-2">
        <h2 className="text=lg font-semibold">Search</h2>
        <SearchBox />
      </section>

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Ask</h2>
        <QABox />
      </section>
    </div>

  );

}
