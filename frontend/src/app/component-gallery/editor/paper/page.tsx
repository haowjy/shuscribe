"use client";

import { useState } from "react";
import { DocumentEditor } from "@/components/editor/DocumentEditor";

export default function PaperEditorPage() {
  const [content, setContent] = useState(`<h1>Paper Mode Document</h1><p>This editor demonstrates the paper-like appearance that makes your content feel like a real document. The paper mode provides realistic page dimensions, margins, and shadows that mimic physical paper.</p><p>Key features of paper mode:</p><ul><li>Realistic page dimensions (A4, Letter, Legal)</li><li>Document-style margins and padding</li><li>Paper-like shadows and appearance</li><li>Print-friendly styling</li><li>Responsive design for mobile devices</li><li>Automatic page breaks when content overflows</li></ul><blockquote><p>"The best writing happens when you feel like you're working with real paper." - Anonymous</p></blockquote><p>Try typing here to experience the paper-like editing environment. Notice how the content is constrained to realistic page dimensions, creating a more focused writing experience.</p><p>When automatic pagination is enabled, content will automatically flow to new pages with visual breaks when it exceeds the page height - just like in real document editors!</p><p>Continue typing to see how the automatic page breaks work. Add more paragraphs, lists, and content to fill up the page and see the automatic pagination in action.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p><p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>`);
  const [paperSize, setPaperSize] = useState<boolean | 'A4' | 'letter' | 'legal'>(true);
  const [autoPagination, setAutoPagination] = useState(false);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Paper Mode Editor</h2>
        <p className="text-muted-foreground mb-6">
          Document editor with realistic paper-like appearance and page dimensions for focused writing.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <DocumentEditor
            content={content}
            placeholder="Start writing your document..."
            onUpdate={(newContent) => {
              setContent(newContent);
              console.log("Paper content:", newContent);
            }}
            paperMode={paperSize}
            autoPagination={autoPagination}
            className="w-full"
          />
        </div>

        <div className="space-y-6">
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Automatic Pagination</h3>
            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={autoPagination}
                  onChange={(e) => setAutoPagination(e.target.checked)}
                  className="text-primary"
                />
                <span className="text-sm">Enable automatic page breaks</span>
              </label>
              <p className="text-xs text-muted-foreground">
                When enabled, content automatically flows to new pages with visual gaps when it exceeds the page height.
              </p>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Page Size</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="paperSize"
                  checked={paperSize === true}
                  onChange={() => setPaperSize(true)}
                  className="text-primary"
                />
                <span className="text-sm">Default (A4)</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="paperSize"
                  checked={paperSize === 'A4'}
                  onChange={() => setPaperSize('A4')}
                  className="text-primary"
                />
                <span className="text-sm">A4 (21 × 29.7 cm)</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="paperSize"
                  checked={paperSize === 'letter'}
                  onChange={() => setPaperSize('letter')}
                  className="text-primary"
                />
                <span className="text-sm">Letter (8.5 × 11 in)</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="paperSize"
                  checked={paperSize === 'legal'}
                  onChange={() => setPaperSize('legal')}
                  className="text-primary"
                />
                <span className="text-sm">Legal (8.5 × 14 in)</span>
              </label>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Paper Features</h3>
            <div className="text-sm space-y-2">
              <div>📄 <strong>Realistic Dimensions:</strong> True-to-life page sizes</div>
              <div>🖼️ <strong>Paper Shadows:</strong> Subtle depth and elevation</div>
              <div>📏 <strong>Document Margins:</strong> Professional spacing</div>
              <div>📄 <strong>Auto Pagination:</strong> Automatic page breaks with gaps</div>
              <div>🖨️ <strong>Print Ready:</strong> Optimized for printing</div>
              <div>📱 <strong>Responsive:</strong> Adapts to mobile screens</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Use Cases</h3>
            <div className="text-sm space-y-2 text-muted-foreground">
              <div>• Academic papers and essays</div>
              <div>• Business documents and reports</div>
              <div>• Creative writing and novels</div>
              <div>• Technical documentation</div>
              <div>• Letters and formal communications</div>
              <div>• Print-ready content creation</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Configuration</h3>
            <div className="bg-muted rounded p-3">
              <pre className="text-xs text-muted-foreground">
{`// Basic paper mode
paperMode={true}
autoPagination={false}

// With automatic pagination
paperMode="A4"
autoPagination={true}

// Specific page sizes
paperMode="A4"      // 21 × 29.7 cm
paperMode="letter"  // 8.5 × 11 in  
paperMode="legal"   // 8.5 × 14 in

// Note: autoPagination requires paperMode`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}