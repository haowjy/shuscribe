"use client";

import { DocumentEditor } from "@/components/editor/DocumentEditor";

export default function ChatEditorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Lightweight Chat Editor</h2>
        <p className="text-muted-foreground mb-6">
          Streamlined editor optimized for messaging interfaces with essential formatting only.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <DocumentEditor
            placeholder="Type a message..."
            onUpdate={(newContent) => {
              console.log("Chat content:", newContent);
            }}
            editable={false}
            toolbar={{
              show: false,
            }}
            footer={{ show: false }}
            className="w-full"
          />
        </div>

        <div className="space-y-6">
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Chat Features</h3>
            <div className="text-sm space-y-2">
              <div>💬 <strong>Quick Formatting:</strong> Bold, italic, and highlighting</div>
              <div>📋 <strong>Lists:</strong> Bullet and numbered lists</div>
              <div>↔️ <strong>Alignment:</strong> Left, center, right alignment</div>
              <div>⏮️ <strong>History:</strong> Undo and redo support</div>
              <div>🎯 <strong>Focused:</strong> No footer clutter for clean UI</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Use Cases</h3>
            <div className="text-sm space-y-2 text-muted-foreground">
              <div>• Messaging applications</div>
              <div>• Comment systems</div>
              <div>• Quick reply interfaces</div>
              <div>• Live chat widgets</div>
              <div>• Social media posts</div>
              <div>• Forum responses</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Configuration</h3>
            <div className="bg-muted rounded p-3">
              <pre className="text-xs text-muted-foreground">
{`toolbar={{
  sections: [
    "history", 
    "formatting", 
    "lists", 
    "alignment"
  ],
  commands: [
    "undo", "redo",
    "toggleBold", "toggleItalic",
    "toggleHighlight",
    "toggleBulletList",
    "toggleOrderedList",
    "setTextAlign"
  ]
}}
footer={{ show: false }}`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}