import { InferAgentUIMessage, ToolLoopAgent, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const DEFAULT_MODEL = process.env.OPENAI_MODEL ?? "gpt-5";

export const chatAgent = new ToolLoopAgent({
  model: openai(DEFAULT_MODEL),
  experimental_telemetry: {
    isEnabled: true,
    recordInputs: true,
    recordOutputs: true,
    functionId: "chat-agent",
    metadata: {
      appArea: "support-chat",
      route: "/api/chat",
    },
  },
  instructions: `You are Relay, a helpful product support assistant inside a demo chat app.

Use the available tools whenever they match the user's request:
- Use lookupOrderStatus for order or shipment questions.
- Use searchKnowledgeBase for questions about docs, onboarding, refunds, or product guidance.
- Use scheduleFollowUp when the user wants a callback, follow-up, or support handoff.

The tool results in this environment are mocked. After using a tool, explain the result naturally and be transparent that it is placeholder data.`,
  tools: {
    lookupOrderStatus: tool({
      description: "Look up a customer's order and return a mocked fulfillment update.",
      inputSchema: z.object({
        orderId: z.string().min(1).describe("The order number to check."),
      }),
      execute: async ({ orderId }) => {
        const normalized = orderId.trim();
        const statusOptions = ["processing", "packed", "in transit", "out for delivery"];
        const status = statusOptions[normalized.length % statusOptions.length];

        return {
          orderId: normalized,
          status,
          eta: status === "processing" ? "Later this week" : "Tomorrow by 5 PM ET",
          lastUpdate: "Today at 10:14 AM ET",
          note: "This is a mock fulfillment record used for early UI development.",
        };
      },
    }),
    searchKnowledgeBase: tool({
      description: "Search the internal help center and return mocked article matches.",
      inputSchema: z.object({
        topic: z.string().min(1).describe("The topic or question to search for."),
      }),
      execute: async ({ topic }) => {
        const query = topic.toLowerCase();
        const library = [
          {
            title: "First-day onboarding checklist",
            snippet: "Connect your workspace, invite teammates, and confirm notification preferences before your first live chat.",
          },
          {
            title: "Billing and refunds",
            snippet: "Refund requests are reviewed within two business days and routed through the support desk.",
          },
          {
            title: "Workspace setup guide",
            snippet: "Start with branding, canned replies, and a shared escalation policy so the assistant can behave consistently.",
          },
        ];

        const matches = library.filter((entry) => {
          const haystack = `${entry.title} ${entry.snippet}`.toLowerCase();
          return query
            .split(/\s+/)
            .some((token) => token.length > 2 && haystack.includes(token));
        });

        return {
          topic,
          summary:
            matches.length > 0
              ? `Found ${matches.length} mocked help-center matches for "${topic}".`
              : `No direct article matched "${topic}", so this mock search returned general setup guidance instead.`,
          matches: matches.length > 0 ? matches : library.slice(0, 2),
        };
      },
    }),
    scheduleFollowUp: tool({
      description: "Create a mocked support follow-up or callback booking.",
      inputSchema: z.object({
        customerName: z.string().min(1).describe("The customer or teammate to follow up with."),
        reason: z.string().min(1).describe("Why the follow-up is needed."),
        channel: z
          .enum(["email", "phone", "video"])
          .default("email")
          .describe("The follow-up channel."),
      }),
      execute: async ({ customerName, reason, channel }) => ({
        customerName,
        reason,
        channel,
        scheduledFor: "Tomorrow at 10:30 AM ET",
        confirmationId: `demo-${customerName.toLowerCase().replace(/[^a-z0-9]+/g, "-") || "guest"}-241`,
        note: "This follow-up is mocked and not connected to a real scheduling system.",
      }),
    }),
  },
});

export type ChatUIMessage = InferAgentUIMessage<typeof chatAgent>;
