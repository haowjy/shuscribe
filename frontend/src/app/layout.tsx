import type { Metadata } from "next";
import Link from "next/link";
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
        <header className="border-b border-border">
          <div className="container mx-auto h-14 px-4 flex items-center justify-between">
            <Link href="/" className="font-semibold text-foreground">ShuScribe</Link>
            {showGallery && (
              <Link
                href="/component-gallery"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Component Gallery
              </Link>
            )}
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}