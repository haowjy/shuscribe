"use client";

import { useState } from "react";
import { TiptapEditor } from "@/components/editor/tiptap-editor";
import CustomizationPanel from "../../_components/CustomizationPanel";
import VariantsPanel from "../../_components/VariantsPanel";
import LiveHtmlPanel from "../../_components/LiveHtmlPanel";
import TipsPanel from "../../_components/TipsPanel";

export default function FullEditorPage() {
  const [content, setContent] = useState("");

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Full-Featured Editor</h2>
        <p className="text-muted-foreground mb-6">
          Complete editor with all toolbar sections and features enabled.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <TiptapEditor
            placeholder="Start typing to test all editor features..."
            onUpdate={(newContent) => {
              setContent(newContent);
              console.log("Content updated:", newContent);
            }}
            className="w-full"
          />
        </div>

        <div className="space-y-6">
          <CustomizationPanel />
          <VariantsPanel />
          <LiveHtmlPanel content={content} />
          <TipsPanel />
        </div>
      </div>
    </div>
  );
}