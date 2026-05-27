"use client";

import { useState } from "react";

const defaultPrompt = "Use the random_number tool, then tell me the number it returned.";

export default function Home() {
  const [model, setModel] = useState("sonnet");
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [output, setOutput] = useState("Ready.");
  const [running, setRunning] = useState(false);

  async function runPrompt() {
    setRunning(true);
    setOutput("Running...");

    try {
      const response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, prompt })
      });
      const data = await response.json();

      setOutput(JSON.stringify(data, null, 2));
    } catch (error) {
      setOutput(JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2));
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="shell">
      <header>
        <h1>Claude PromptLayer Lab</h1>
        <p>One route, one SDK call, PromptLayer tracing enabled through code.</p>
      </header>

      <section className="panel">
        <label>
          Model
          <input value={model} onChange={(event) => setModel(event.target.value)} />
        </label>

        <label>
          Prompt
          <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} />
        </label>

        <button className="primary" onClick={runPrompt} disabled={running || !prompt.trim()}>
          {running ? "Running..." : "Run"}
        </button>
      </section>

      <section className="output">
        <div className="panelHead">
          <h2>Output</h2>
          <button onClick={() => setOutput("Ready.")}>Clear</button>
        </div>
        <pre>{output}</pre>
      </section>
    </main>
  );
}
