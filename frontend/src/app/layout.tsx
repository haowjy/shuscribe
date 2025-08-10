import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShuScribe - Universe Content Management",
  description: "Frontend-centric Universe Content Management Platform built with Next.js 15 + React 19",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}