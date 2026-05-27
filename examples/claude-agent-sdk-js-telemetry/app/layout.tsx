import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Claude PromptLayer Next App",
  description: "Local manual tester for Claude Agent SDK plus PromptLayer."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
