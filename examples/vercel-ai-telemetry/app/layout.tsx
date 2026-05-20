import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Relay Chat Demo",
  description: "A simple AI SDK chat app with an OpenAI-backed agent and mock tools.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
