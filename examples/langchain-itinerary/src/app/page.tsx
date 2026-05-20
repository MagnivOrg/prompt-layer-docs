import { ChatClient } from "./chat-client";

export default function Home() {
  return (
    <main className="page">
      <section className="shell">
        <div className="header">
          <p className="eyebrow">Pocket Trip Pal</p>
          <h1>Chatty itinerary doodler</h1>
        </div>

        <p className="subtitle">
          In-memory chat with server-side LangChain calls through a traced API route.
        </p>

        {/* Client state is isolated here; secrets, tools, and tracing stay on the server route. */}
        <ChatClient />
      </section>
    </main>
  );
}
