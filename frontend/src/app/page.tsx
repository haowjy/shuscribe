import Link from "next/link";
import { FileText, TestTube, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-foreground mb-4">
            ShuScribe
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Universe Content Management Platform
          </p>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Frontend-centric content management built with Next.js 15 + React 19, 
            featuring a comprehensive Tiptap editor for rich text editing and universe building.
          </p>
        </div>

        {/* Navigation Cards */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Editor Test */}
          <Link 
            href="/editor-test"
            className="group bg-card border border-border rounded-lg p-8 hover:border-primary/50 transition-all duration-300 hover:shadow-lg"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                <FileText size={24} className="text-primary" />
              </div>
              <h2 className="text-2xl font-semibold">Editor Test</h2>
            </div>
            <p className="text-muted-foreground mb-4">
              Test the Tiptap editor with comprehensive formatting, structure, and advanced features.
            </p>
            <div className="flex items-center text-primary group-hover:translate-x-1 transition-transform">
              <span className="mr-2">Test Editor</span>
              <ArrowRight size={16} />
            </div>
          </Link>

          {/* Development Hub */}
          <div className="bg-card border border-border rounded-lg p-8 opacity-60">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-muted rounded-lg">
                <TestTube size={24} className="text-muted-foreground" />
              </div>
              <h2 className="text-2xl font-semibold text-muted-foreground">Test Suite</h2>
            </div>
            <p className="text-muted-foreground mb-4">
              Comprehensive testing suite for components, accessibility, and responsive design.
            </p>
            <div className="text-muted-foreground">
              <span>Coming Soon</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground">
            Built with Next.js 15, React 19, TypeScript, and Tiptap
          </p>
        </div>
      </div>
    </div>
  );
}