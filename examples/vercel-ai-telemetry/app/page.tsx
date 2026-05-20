"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { useState } from "react";
import type { ChatUIMessage } from "@/lib/chat-agent";
import styles from "./page.module.css";

const starterPrompts = [
  {
    label: "Track an order",
    prompt: "Can you check the status of order 2048 for me?",
  },
  {
    label: "Search docs",
    prompt: "What does your onboarding guide say about first-day setup?",
  },
  {
    label: "Book a follow-up",
    prompt: "Schedule a support callback for Sam about billing questions.",
  },
] as const;

export default function Home() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status, error } = useChat<ChatUIMessage>({
    transport: new DefaultChatTransport({
      api: "/api/chat",
    }),
  });

  const isBusy = status === "submitted" || status === "streaming";

  let helperLabel = "Try one of the prompts to watch the agent use mocked tools.";

  if (status === "submitted") {
    helperLabel = "Sending your message...";
  } else if (status === "streaming") {
    helperLabel = "The agent is thinking and may call tools.";
  } else if (error) {
    helperLabel = "The last request failed. Check your env vars and try again.";
  }

  function submitMessage(message: string) {
    const trimmed = message.trim();

    if (!trimmed || isBusy) {
      return;
    }

    void sendMessage({ text: trimmed });
    setInput("");
  }

  return (
    <div className={styles.page}>
      <main className={styles.shell}>
        <section className={styles.sidebar}>
          <span className={styles.eyebrow}>OpenAI + Vercel AI SDK</span>
          <h1>Relay is a starter chat surface with an agent and mock tools.</h1>
          <p className={styles.lead}>
            The UI streams model output, the agent decides when to call tools,
            and each tool returns deterministic fake data so we can shape the
            product before connecting real systems.
          </p>

          <div className={styles.note}>
            <strong>Setup</strong>
            <p>
              Add <code>OPENAI_API_KEY</code> to <code>.env.local</code>. You
              can optionally set <code>OPENAI_MODEL</code>; this demo defaults
              to <code>gpt-5</code> based on the current AI SDK OpenAI provider
              docs.
            </p>
          </div>

          <div className={styles.starterList}>
            {starterPrompts.map((prompt) => (
              <button
                key={prompt.label}
                className={styles.starter}
                disabled={isBusy}
                onClick={() => submitMessage(prompt.prompt)}
                type="button"
              >
                <span>{prompt.label}</span>
                <small>{prompt.prompt}</small>
              </button>
            ))}
          </div>
        </section>

        <section className={styles.chatPanel}>
          <header className={styles.chatHeader}>
            <div>
              <span className={styles.chatTitle}>Chat Session</span>
              <p>{helperLabel}</p>
            </div>
            <span
              className={`${styles.statusBadge} ${
                isBusy ? styles.statusBusy : styles.statusReady
              }`}
            >
              {status}
            </span>
          </header>

          <div className={styles.messages}>
            {messages.length === 0 ? (
              <div className={styles.emptyState}>
                <p>Start with a prompt that asks for a lookup, doc search, or follow-up.</p>
                <small>
                  The agent instructions encourage tool use for those requests,
                  and the tool responses are mocked for now.
                </small>
              </div>
            ) : null}

            {messages.map((message) => (
              <article
                key={message.id}
                className={`${styles.message} ${
                  message.role === "user" ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageMeta}>
                  {message.role === "user" ? "You" : "Relay"}
                </div>

                <div className={styles.messageBody}>
                  {message.parts.map((part, index) => {
                    const key = `${message.id}-${index}`;

                    switch (part.type) {
                      case "text":
                        return part.text ? (
                          <p key={key} className={styles.messageText}>
                            {part.text}
                          </p>
                        ) : null;

                      case "tool-lookupOrderStatus":
                        return (
                          <div key={key} className={styles.toolCard}>
                            <span className={styles.toolLabel}>Mock tool · order status</span>
                            {part.state === "input-streaming" ? (
                              <p>Gathering order details...</p>
                            ) : null}
                            {part.state === "input-available" ? (
                              <p>Checking order <code>{part.input.orderId}</code>...</p>
                            ) : null}
                            {part.state === "output-available" ? (
                              <>
                                <p>
                                  Order <code>{part.output.orderId}</code> is{" "}
                                  <strong>{part.output.status}</strong>.
                                </p>
                                <p className={styles.toolMeta}>
                                  ETA: {part.output.eta} · Last update: {part.output.lastUpdate}
                                </p>
                                <p className={styles.toolMeta}>{part.output.note}</p>
                              </>
                            ) : null}
                            {part.state === "output-error" ? (
                              <p className={styles.errorText}>{part.errorText}</p>
                            ) : null}
                          </div>
                        );

                      case "tool-searchKnowledgeBase":
                        return (
                          <div key={key} className={styles.toolCard}>
                            <span className={styles.toolLabel}>Mock tool · knowledge search</span>
                            {part.state === "input-streaming" ? (
                              <p>Scanning the help center...</p>
                            ) : null}
                            {part.state === "input-available" ? (
                              <p>Searching for <code>{part.input.topic}</code>...</p>
                            ) : null}
                            {part.state === "output-available" ? (
                              <>
                                <p>{part.output.summary}</p>
                                <ul className={styles.toolList}>
                                  {part.output.matches.map((match) => (
                                    <li key={match.title}>
                                      <strong>{match.title}</strong>
                                      <span>{match.snippet}</span>
                                    </li>
                                  ))}
                                </ul>
                              </>
                            ) : null}
                            {part.state === "output-error" ? (
                              <p className={styles.errorText}>{part.errorText}</p>
                            ) : null}
                          </div>
                        );

                      case "tool-scheduleFollowUp":
                        return (
                          <div key={key} className={styles.toolCard}>
                            <span className={styles.toolLabel}>Mock tool · follow-up booking</span>
                            {part.state === "input-streaming" ? (
                              <p>Preparing a mock follow-up...</p>
                            ) : null}
                            {part.state === "input-available" ? (
                              <p>
                                Booking a {part.input.channel} follow-up for{" "}
                                <code>{part.input.customerName}</code>.
                              </p>
                            ) : null}
                            {part.state === "output-available" ? (
                              <>
                                <p>
                                  Placeholder booking created for {part.output.customerName}.
                                </p>
                                <p className={styles.toolMeta}>
                                  {part.output.channel} · {part.output.scheduledFor}
                                </p>
                                <p className={styles.toolMeta}>
                                  Confirmation: <code>{part.output.confirmationId}</code>
                                </p>
                              </>
                            ) : null}
                            {part.state === "output-error" ? (
                              <p className={styles.errorText}>{part.errorText}</p>
                            ) : null}
                          </div>
                        );

                      default:
                        return null;
                    }
                  })}
                </div>
              </article>
            ))}
          </div>

          <form
            className={styles.composer}
            onSubmit={(event) => {
              event.preventDefault();
              submitMessage(input);
            }}
          >
            <label className={styles.inputFrame}>
              <span className={styles.inputLabel}>Message</span>
              <textarea
                className={styles.input}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask about an order, docs, or a support callback..."
                rows={3}
              />
            </label>

            <div className={styles.composerFooter}>
              <p className={styles.composerHint}>
                Tool calls are mocked, so this is safe to explore while we shape the product.
              </p>
              <button className={styles.sendButton} disabled={isBusy || !input.trim()} type="submit">
                {isBusy ? "Working..." : "Send"}
              </button>
            </div>

            {error ? <p className={styles.errorText}>{error.message}</p> : null}
          </form>
        </section>
      </main>
    </div>
  );
}
