"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, FileText, Download, Upload } from "lucide-react";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-semibold">ShuScribe</h1>
            </div>
            <div className="flex items-center gap-2">
              <Link href="/auth/login">
                <Button variant="ghost" size="sm">
                  Login
                </Button>
              </Link>
              <Link href="/auth/signup">
                <Button size="sm">
                  Try Free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/5 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-primary/3 rounded-full blur-2xl"></div>
        </div>
        
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-1 rounded-full text-sm mb-6 animate-slide-up">
            ✨ MVP Launch - Start building your universe today
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 animate-slide-up">
            Write Stories, Build Wikis
            <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent"> Automatically</span>
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-slide-up">
            Type <code className="bg-muted px-2 py-1 rounded text-primary">@character/elara</code> → Get instant universe wikis. 
            <br />Like Scrivener + Notion, but understands your story automatically.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up">
            <Link href="/auth/signup">
              <Button size="lg" className="gap-2 bg-gradient-to-r from-primary to-primary/90 hover:from-primary/90 hover:to-primary/80">
                <BookOpen className="h-5 w-5" />
                Start Writing Free
              </Button>
            </Link>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="flex -space-x-1">
                <div className="w-6 h-6 bg-primary/20 rounded-full border-2 border-background"></div>
                <div className="w-6 h-6 bg-primary/30 rounded-full border-2 border-background"></div>
                <div className="w-6 h-6 bg-primary/40 rounded-full border-2 border-background"></div>
              </div>
              <span>Join 1000+ writers building universes</span>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-2xl font-semibold text-center mb-8">
          See How It Works
        </h2>
        
        {/* Mock Workspace Interface */}
        <Card className="p-6 mb-8 overflow-hidden">
          <div className="bg-muted/50 rounded-lg p-4">
            <div className="text-xs text-muted-foreground mb-4 text-center">
              Live Workspace Preview
            </div>
            
            {/* Mock 3-panel layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-80 text-xs">
              {/* File Explorer */}
              <div className="lg:col-span-3 bg-background rounded border p-3">
                <div className="font-medium mb-2 text-foreground">📁 My Fantasy Novel</div>
                <div className="space-y-1 text-muted-foreground">
                  <div className="pl-2">📁 characters</div>
                  <div className="pl-4">👥 elara.md</div>
                  <div className="pl-4">💀 villain.md</div>
                  <div className="pl-2">📁 locations</div>
                  <div className="pl-4">🏛️ taverns</div>
                  <div className="pl-6 text-primary">→ prancing-pony.md</div>
                  <div className="pl-2">📁 chapters</div>
                  <div className="pl-4">📝 chapter-01.md</div>
                </div>
              </div>
              
              {/* Editor */}
              <div className="lg:col-span-6 bg-background rounded border p-3 relative">
                <div className="border-b pb-2 mb-3 flex items-center justify-between">
                  <span className="text-xs bg-muted px-2 py-1 rounded">chapter-01.md</span>
                  <span className="text-xs text-muted-foreground">Auto-saved • 247 words</span>
                </div>
                <div className="font-mono text-sm leading-relaxed">
                  <div className="mb-2 text-muted-foreground">The fire crackled in the hearth as</div>
                  <div className="mb-2">
                    <span className="text-primary bg-primary/10 px-1 rounded">@character/elara</span> walked into
                  </div>
                  <div className="relative">
                    <span>the @<span className="typing-cursor"></span></span>
                    <div className="inline-block relative">
                      <div className="absolute top-6 left-0 bg-background border rounded shadow-lg p-3 z-10 w-52 animate-fade-in">
                        <div className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <div className="w-1 h-1 bg-green-500 rounded-full animate-pulse"></div>
                          instant suggestions:
                        </div>
                        <div className="space-y-1.5">
                          <div className="flex items-center gap-2 text-primary cursor-pointer hover:bg-primary/10 px-2 py-1 rounded transition-colors">
                            📄 <span className="font-medium">@tavern/prancing-pony</span>
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground hover:bg-muted px-2 py-1 rounded transition-colors">
                            📍 @location/hometown
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground hover:bg-muted px-2 py-1 rounded transition-colors">
                            🏷️ @fire-magic <span className="text-xs">(3 docs)</span>
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-2 pt-2 border-t">
                          ↵ to select • esc to cancel
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 text-muted-foreground text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse-slow"></div>
                      AI context building...
                    </div>
                  </div>
                </div>
              </div>
              
              {/* AI Panel */}
              <div className="lg:col-span-3 bg-background rounded border p-3">
                <div className="font-medium mb-2 text-foreground">AI Context</div>
                <div className="space-y-2 text-muted-foreground">
                  <div className="text-xs">Current context:</div>
                  <div className="bg-muted/50 rounded p-2 text-xs">
                    • Elara (protagonist)
                    • Fire magic theme
                    • Tavern setting
                  </div>
                  <div className="text-xs mt-3">Auto-generated:</div>
                  <div className="bg-primary/10 rounded p-2 text-xs">
                    📖 Character wiki
                    📍 Location wiki
                    🎯 Plot connections
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
        
        {/* Step by step explanation */}
        <div className="grid md:grid-cols-2 gap-8">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Badge variant="secondary" className="text-lg px-3 py-1">1</Badge>
              <h3 className="font-medium">Type @-references naturally</h3>
            </div>
            <div className="space-y-3">
              <div className="bg-muted p-3 rounded-lg font-mono text-sm">
                Elara walked into the <span className="text-primary">@tavern/prancing-pony</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Just type @ and get instant autocomplete for characters, locations, and themes. No manual linking needed.
              </p>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Badge variant="secondary" className="text-lg px-3 py-1">2</Badge>
              <h3 className="font-medium">Get instant wikis</h3>
            </div>
            <div className="space-y-3">
              <div className="bg-gradient-to-r from-primary/10 to-primary/5 p-3 rounded-lg">
                <div className="text-sm font-medium mb-1">Auto-generated Wiki:</div>
                <div className="text-xs text-muted-foreground">
                  ✨ Character profiles, location details, plot connections
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                AI analyzes your @-references and builds comprehensive wikis automatically. Export to PDF, EPUB, or publish online.
              </p>
            </div>
          </Card>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          Four Key Features That Set Us Apart
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-primary/20 hover:border-primary/40">
            <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">@-Reference System</h3>
            <p className="text-sm text-muted-foreground">
              Type @character/name for instant linking. No manual work needed.
            </p>
            <div className="mt-4 text-xs text-primary/70">
              ⚡ Instant autocomplete
            </div>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-primary/20 hover:border-primary/40">
            <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <BookOpen className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Auto Wiki Generation</h3>
            <p className="text-sm text-muted-foreground">
              One-click comprehensive wikis from your natural writing.
            </p>
            <div className="mt-4 text-xs text-primary/70">
              🤖 AI-powered analysis
            </div>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-primary/20 hover:border-primary/40">
            <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Download className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Export to PDF/EPUB</h3>
            <p className="text-sm text-muted-foreground">
              Publish anywhere with multiple format exports.
            </p>
            <div className="mt-4 text-xs text-primary/70">
              📄 Multiple formats
            </div>
          </Card>

          <Card className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-primary/20 hover:border-primary/40">
            <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Upload className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Simple Publishing</h3>
            <p className="text-sm text-muted-foreground">
              Share your stories with integrated wiki access.
            </p>
            <div className="mt-4 text-xs text-primary/70">
              🌐 Online sharing
            </div>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-muted/30 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Build Your Universe?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join writers who are already creating comprehensive story worlds automatically.
          </p>
          <Link href="/auth/signup">
            <Button size="lg" className="gap-2">
              <BookOpen className="h-5 w-5" />
              Start Writing Free
            </Button>
          </Link>
          <p className="text-sm text-muted-foreground mt-4">
            No credit card required • Get started in 30 seconds
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              © 2024 ShuScribe. The operating system for fictional universes.
            </p>
            <div className="flex items-center gap-4">
              <Link href="/auth/login" className="text-sm text-muted-foreground hover:text-foreground">
                Login
              </Link>
              <Link href="/auth/signup" className="text-sm text-primary hover:underline">
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}