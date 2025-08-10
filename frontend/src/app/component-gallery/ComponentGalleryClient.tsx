"use client";

import { useState } from "react";
import { TiptapEditor } from "@/components/editor/tiptap-editor";

export default function ComponentGalleryClient() {
  const [content, setContent] = useState("");

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <h1 className="text-3xl font-bold mb-8">Component Gallery</h1>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div>
              <h2 className="text-2xl font-semibold mb-4">Full-Featured Editor</h2>
              <TiptapEditor
                placeholder="Start typing to test all editor features..."
                onUpdate={(newContent) => {
                  setContent(newContent);
                  console.log("Content updated:", newContent);
                }}
                className="w-full"
              />
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Lightweight Chat Editor</h2>
              <TiptapEditor
                placeholder="Type a message..."
                onUpdate={(newContent) => {
                  console.log("Chat content:", newContent);
                }}
                toolbar={{
                  sections: ["history", "formatting", "lists", "alignment"],
                  commands: [
                    "undo",
                    "redo",
                    "toggleBold",
                    "toggleItalic",
                    "toggleHighlight",
                    "toggleBulletList",
                    "toggleOrderedList",
                    "setTextAlign",
                  ],
                }}
                footer={{ show: false }}
                className="w-full"
              />
            </div>

            <div>
              <h2 className="text-2xl font-semibold mb-4">Minimal Notes Editor</h2>
              <TiptapEditor
                placeholder="Add a quick note..."
                toolbar={{
                  sections: ["formatting"],
                  commands: ["toggleBold", "toggleItalic"],
                }}
                footer={{
                  showCharacterCount: false,
                  showWordCount: false,
                }}
                className="w-full"
              />
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-card border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-3">Customization Features</h3>
              <div className="text-sm space-y-2">
                <div>✅ <strong>Toolbar Sections:</strong> Choose which sections to include (history, textStyle, formatting, lists, alignment, blocks, insert, table)</div>
                <div>✅ <strong>Individual Commands:</strong> Select specific commands to show (toggleBold, toggleItalic, etc.)</div>
                <div>✅ <strong>Footer Config:</strong> Toggle character count, word count, stats</div>
                <div>✅ <strong>Extension Overrides:</strong> Customize highlight, link, table behaviors</div>
                <div>✅ <strong>Composition Pattern:</strong> Use hooks and primitives for custom editors</div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-3">Editor Variants</h3>
              <div className="text-sm space-y-2">
                <div>📝 <strong>Full Editor:</strong> All features enabled</div>
                <div>💬 <strong>Chat Editor:</strong> Basic formatting only</div>
                <div>📄 <strong>Notes Editor:</strong> Minimal toolbar</div>
                <div>🎯 <strong>Custom:</strong> Use hooks for complete control</div>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-3">Live HTML Output</h3>
              <div className="bg-muted rounded p-3 max-h-60 overflow-y-auto">
                <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                  {content || "No content yet... Start typing in the editor to see the HTML output here."}
                </pre>
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4">
              <h3 className="font-semibold mb-3">Quick Tips</h3>
              <div className="text-sm space-y-2 text-muted-foreground">
                <div>• Use toolbar buttons for all formatting</div>
                <div>• Active formatting shows highlighted buttons</div>
                <div>• Try task lists with checkboxes</div>
                <div>• Insert tables with resizable columns</div>
                <div>• Text alignment works on headings too</div>
                <div>• Link/image prompts for URLs</div>
                <div>• Character count updates live</div>
                <div>• All keyboard shortcuts still work!</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
