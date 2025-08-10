import type { Metadata } from "next";
import ConditionalHeader from "@/components/layout/ConditionalHeader";
import { AuthProvider } from "@/contexts/AuthContext";
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
  const showGallery =
    process.env.NODE_ENV === "development" ||
    process.env.NEXT_PUBLIC_ENABLE_COMPONENT_GALLERY === "true";

  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        <AuthProvider>
          <ConditionalHeader showGallery={showGallery}>
            {children}
          </ConditionalHeader>
        </AuthProvider>
      </body>
    </html>
  );
}