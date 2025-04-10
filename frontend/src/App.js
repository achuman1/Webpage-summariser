import React, { useState } from "react";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSummarize = async () => {
    setLoading(true);
    setError("");
    setSections([]);

    try {
      const response = await fetch("https://webpage-summariser-backend.onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (response.ok) {
        setSections(data.sections);
      } else {
        setError(data.error || "Something went wrong.");
      }
    } catch (err) {
      setError("Could not connect to backend.");
    }

    setLoading(false);
  };

  const handleDownloadPDF = async () => {
    const response = await fetch("https://webpage-summariser-backend.onrender.com", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sections }),
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "summary.pdf";
    a.click();
  };

  return (
    <div className="App">
      <h1>Webpage Summariser</h1>

      <input
        type="text"
        placeholder="Enter webpage URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button onClick={handleSummarize} disabled={loading || !url}>
        {loading ? "Summarizing..." : "Summarize"}
      </button>

      {error && <p className="error">{error}</p>}

      {sections.length > 0 && (
        <>
          <button onClick={handleDownloadPDF} className="download-button">
            📄 Download PDF
          </button>

          <h2>Section-wise Summary</h2>
          <div className="summary-box">
            {sections.map((sec, idx) => (
              <div className="section" key={idx}>
                <h3>{sec.section}</h3>
                <p>{sec.summary}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
