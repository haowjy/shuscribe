import Link from "next/link";
import { ArrowRight, FileText, Layers, Wand2 } from "lucide-react";

export default function HomePage() {
  const showGallery =
    process.env.NODE_ENV === "development" ||
    process.env.NEXT_PUBLIC_ENABLE_COMPONENT_GALLERY === "true";

  return (
    <div className="min-h-screen bg-background">
      <section className="container mx-auto px-4 py-20 max-w-5xl text-center">
        <h1 className="text-6xl font-bold text-foreground mb-6">ShuScribe</h1>
        <p className="text-xl text-muted-foreground mb-3">
          Universe Content Management — from indie creators to studios
        </p>
        <p className="text-muted-foreground max-w-2xl mx-auto mb-10">
          "Cursor for fiction writing" powered by context-aware <span className="font-medium">@-references</span>
          and one-click <span className="font-medium">AI wiki generation</span>. Build coherent worlds, keep
          continuity, and publish with confidence.
        </p>
        <div className="flex items-center justify-center gap-3">
          <a
            href="#features"
            className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-4 py-2 text-foreground hover:border-primary/60 transition"
          >
            Explore Features
            <ArrowRight size={16} />
          </a>
          {showGallery && (
            <Link
              href="/component-gallery"
              className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-primary-foreground hover:opacity-90 transition"
            >
              Open Component Gallery
            </Link>
          )}
        </div>
      </section>

      <section id="features" className="container mx-auto px-4 py-12 max-w-5xl">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="mb-3 text-primary"><FileText size={24} /></div>
            <h3 className="font-semibold mb-2">Context‑Aware Writing</h3>
            <p className="text-sm text-muted-foreground">
              Link characters, locations, and themes inline with <span className="font-medium">@-references</span> and
              instant autocomplete.
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="mb-3 text-primary"><Wand2 size={24} /></div>
            <h3 className="font-semibold mb-2">AI Wiki Generation</h3>
            <p className="text-sm text-muted-foreground">
              Turn references into a structured, spoiler‑safe wiki with one click.
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="mb-3 text-primary"><Layers size={24} /></div>
            <h3 className="font-semibold mb-2">Publish & Export</h3>
            <p className="text-sm text-muted-foreground">
              Validate continuity, then export to Markdown, PDF, and EPUB or publish simple public pages.
            </p>
          </div>
        </div>
      </section>

      <div className="text-center mt-16 pt-8 border-t border-border">
        <p className="text-sm text-muted-foreground">
          Built with Next.js 15, React 19, TypeScript, and Tiptap
        </p>
      </div>
    </div>
  );
}