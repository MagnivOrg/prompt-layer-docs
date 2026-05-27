"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Message = {
  id: number;
  sender: "user" | "bot";
  text: string;
};

type SubmitEventLike = {
  preventDefault: () => void;
};

export function ChatClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);

  function appendMessage(sender: Message["sender"], text: string) {
    // Local-only chat history keeps the demo focused on server tracing, not persistence.
    setMessages((current) => [
      ...current,
      { id: current.length + 1, sender, text },
    ]);
  }

  async function sendMessage(userText: string) {
    if (isSending) {
      return;
    }

    appendMessage("user", userText);
    setDraft("");
    setIsSending(true);

    try {
      // The API route owns validation, OpenAI access, LangChain orchestration, and OTEL spans.
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input: userText,
        }),
      });

      const data = (await response.json()) as { reply?: string; error?: string };
      if (!response.ok) {
        throw new Error(data.error || "The server could not complete the request.");
      }

      const reply = data.reply ?? "";
      appendMessage("bot", reply);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "I hit a server-side issue. Try again.";
      appendMessage("bot", message);
    } finally {
      setIsSending(false);
    }
  }

  async function handleSubmit(event: SubmitEventLike) {
    event.preventDefault();

    // Trim on submit so empty or whitespace-only messages never reach the traced API route.
    const userText = draft.trim();
    if (!userText || isSending) {
      return;
    }

    await sendMessage(userText);
  }

  return (
    <>
      <div className="chat">
        {messages.length === 0 ? (
          <div className="emptyState">
            <div className="emptyCard">
              <span className="badge">starter note</span>
              <p>Nothing here yet. Submit a question below to get started.</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <article
              key={message.id}
              className={message.sender === "bot" ? "botBubble" : "userBubble"}
            >
              <span className="badge">{message.sender === "bot" ? "pal" : "you"}</span>
              {/* Render model/user text as markdown at the UI edge; tracing still records the raw string. */}
              <div className="markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.text}
                </ReactMarkdown>
              </div>
            </article>
          ))
        )}

        {isSending ? (
          <article className="loadingBubble">
            <span className="badge">pal</span>
            <div className="loadingDots" aria-label="Agent is thinking">
              <span />
              <span />
              <span />
            </div>
          </article>
        ) : null}
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <label className="composerLabel" htmlFor="trip-draft">
          Tell me the mood, city, or snack priority
        </label>
        <div className="composerRow">
          <input
            id="trip-draft"
            className="input"
            onChange={(event) => setDraft(event.target.value)}
            placeholder="A cozy three-day escape with maximal pastries..."
            value={draft}
            disabled={isSending}
          />
          <button className="sendButton" type="submit" disabled={isSending}>
            {isSending ? "Planning..." : "Send"}
          </button>
        </div>
      </form>
    </>
  );
}
