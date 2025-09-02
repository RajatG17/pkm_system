import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/files/upload", {
      method: "POST",
      body: formData,
    });

    alert(JSON.stringify(await res.json()));
  };

  return (
    <div className="p-10 margin-auto">
      <h1 className="text-2xl font-bold mb-4">PKM System</h1>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button
        onClick={handleUpload}
        className="ml-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Upload
      </button>
    </div>
  );
}

export default App;
