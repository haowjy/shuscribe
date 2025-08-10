"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { ReactNode } from "react";

interface ConditionalHeaderProps {
  children: ReactNode;
  showGallery: boolean;
}

export default function ConditionalHeader({ children, showGallery }: ConditionalHeaderProps) {
  const pathname = usePathname();
  const isGalleryRoute = pathname.startsWith("/component-gallery");

  if (isGalleryRoute) {
    // Gallery routes: no global header, full-height app experience
    return <>{children}</>;
  }

  // Non-gallery routes: show global header
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b border-border">
        <div className="container mx-auto h-14 px-4 flex items-center justify-between">
          <Link href="/" className="font-semibold text-foreground hover:text-foreground/80 transition-colors">
            ShuScribe
          </Link>
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
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}