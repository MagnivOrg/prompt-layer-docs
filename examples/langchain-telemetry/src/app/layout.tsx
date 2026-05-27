import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pocket Trip Pal",
  description: "A tiny quirky chat interface for itinerary daydreaming.",
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
