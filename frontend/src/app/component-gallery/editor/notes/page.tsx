"use client";

import { DocumentEditor } from "@/components/editor/DocumentEditor";

export default function NotesEditorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Minimal Notes Editor</h2>
        <p className="text-muted-foreground mb-6">
          Ultra-lightweight editor for quick note-taking with only essential formatting.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <DocumentEditor
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

        <div className="space-y-6">
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Minimal Features</h3>
            <div className="text-sm space-y-2">
              <div>✏️ <strong>Basic Formatting:</strong> Bold and italic only</div>
              <div>🚫 <strong>No Footer:</strong> Clean interface without counts</div>
              <div>⚡ <strong>Lightweight:</strong> Fastest loading variant</div>
              <div>🎯 <strong>Focused:</strong> Distraction-free writing</div>
              <div>📱 <strong>Mobile-First:</strong> Perfect for small screens</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Perfect For</h3>
            <div className="text-sm space-y-2 text-muted-foreground">
              <div>• Quick jotting down ideas</div>
              <div>• Simple text input forms</div>
              <div>• Mobile note-taking apps</div>
              <div>• Minimal content editing</div>
              <div>• Todo list descriptions</div>
              <div>• Caption and label editing</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Configuration</h3>
            <div className="bg-muted rounded p-3">
              <pre className="text-xs text-muted-foreground">
{`toolbar={{
  sections: ["formatting"],
  commands: [
    "toggleBold", 
    "toggleItalic"
  ]
}}
footer={{
  showCharacterCount: false,
  showWordCount: false
}}`}
              </pre>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Keyboard Shortcuts</h3>
            <div className="text-sm space-y-2 text-muted-foreground">
              <div><kbd className="px-1.5 py-0.5 text-xs bg-muted-foreground/10 rounded">⌘ B</kbd> Bold</div>
              <div><kbd className="px-1.5 py-0.5 text-xs bg-muted-foreground/10 rounded">⌘ I</kbd> Italic</div>
              <div><kbd className="px-1.5 py-0.5 text-xs bg-muted-foreground/10 rounded">⌘ Z</kbd> Undo</div>
              <div><kbd className="px-1.5 py-0.5 text-xs bg-muted-foreground/10 rounded">⌘ ⇧ Z</kbd> Redo</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}