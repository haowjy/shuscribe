"use client";

import React, { useState } from "react";
import { 
  ResizablePanelGroup, 
  ResizablePanel, 
  ResizableHandle 
} from "@/components/ui/resizable";
import { Button } from "@/components/ui/button";
import { 
  File, 
  User, 
  Globe, 
  Star, 
  Heart, 
  Zap, 
  Shield, 
  Crown 
} from "lucide-react";

const icons = [User, Globe, Star, Heart, Zap, Shield, Crown];

const mockFiles = [
  {
    id: "1",
    name: "character_notes.md",
    tags: [
      { id: "1", name: "Character", icon: "User", color: "#3b82f6" },
      { id: "2", name: "World", icon: "Globe", color: "#10b981" },
      { id: "3", name: "Important", icon: "Star", color: "#f59e0b" }
    ]
  },
  {
    id: "2", 
    name: "very_long_filename_that_should_truncate.md",
    tags: [
      { id: "4", name: "Love", icon: "Heart", color: "#ef4444" },
      { id: "5", name: "Action", icon: "Zap", color: "#8b5cf6" },
      { id: "6", name: "Defense", icon: "Shield", color: "#06b6d4" },
      { id: "7", name: "Royal", icon: "Crown", color: "#f97316" },
      { id: "8", name: "Extra", icon: "Star", color: "#84cc16" }
    ]
  },
  {
    id: "3",
    name: "short.md", 
    tags: [
      { id: "9", name: "Single", icon: "Star", color: "#f59e0b" }
    ]
  }
];

function TagIcon({ tag }: { tag: any }) {
  const IconComponent = icons.find(icon => icon.name === tag.icon) || Star;
  return (
    <div 
      className="w-5 h-5 rounded flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
      style={{ backgroundColor: tag.color }}
      title={tag.name}
    >
      <IconComponent className="w-3 h-3" />
    </div>
  );
}

function TestRowWithButton({ file, maxTags }: { file: any; maxTags: number }) {
  const visibleTags = file.tags.slice(0, maxTags);
  const extraCount = file.tags.length - maxTags;

  return (
    <Button
      variant="tree-item"
      className="w-full h-auto text-sm flex items-center justify-start overflow-hidden px-2 py-1 mb-1"
    >
      <File className="w-4 h-4 mr-2 flex-shrink-0" />
      <span className="flex-1 text-left cursor-inherit overflow-hidden whitespace-nowrap text-ellipsis min-w-0 shrink-[999]">
        {file.name}
      </span>
      <div className="flex gap-1 items-center ml-2 flex-shrink-0">
        {visibleTags.map((tag: any) => (
          <TagIcon key={tag.id} tag={tag} />
        ))}
        {extraCount > 0 && (
          <div className="w-5 h-5 rounded bg-gray-400 flex items-center justify-center text-white text-xs font-bold">
            +{extraCount}
          </div>
        )}
      </div>
    </Button>
  );
}

function TestRowWithDiv({ file, maxTags }: { file: any; maxTags: number }) {
  const visibleTags = file.tags.slice(0, maxTags);
  const extraCount = file.tags.length - maxTags;

  return (
    <div className="w-full h-auto text-sm flex items-center justify-start overflow-hidden px-2 py-1 mb-1 border rounded hover:bg-accent transition-colors">
      <File className="w-4 h-4 mr-2 flex-shrink-0" />
      <span className="flex-1 text-left overflow-hidden whitespace-nowrap text-ellipsis min-w-0">
        {file.name}
      </span>
      <div className="flex gap-1 items-center ml-2 flex-shrink-0">
        {visibleTags.map((tag: any) => (
          <TagIcon key={tag.id} tag={tag} />
        ))}
        {extraCount > 0 && (
          <div className="w-5 h-5 rounded bg-gray-400 flex items-center justify-center text-white text-xs font-bold">
            +{extraCount}
          </div>
        )}
      </div>
    </div>
  );
}

export default function TagCollapseMockPage() {
  const [panelSize, setPanelSize] = useState(30);

  const getMaxTags = (size: number) => {
    if (size > 40) return 3;
    if (size > 25) return 2;
    return 1;
  };

  const maxTags = getMaxTags(panelSize);

  return (
    <div className="h-screen w-full p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-2">Tag Collapse Test</h1>
        <p className="text-sm text-muted-foreground mb-4">
          Panel size: {panelSize.toFixed(1)}% | Max tags: {maxTags}
        </p>
      </div>

      <ResizablePanelGroup direction="horizontal" className="h-[600px] border rounded">
        <ResizablePanel 
          defaultSize={30} 
          minSize={15}
          onResize={(size) => setPanelSize(size)}
        >
          <div className="h-full overflow-auto">
            <div className="p-4">
              <h2 className="font-semibold mb-4">With Button Component</h2>
              {mockFiles.map(file => (
                <TestRowWithButton key={`btn-${file.id}`} file={file} maxTags={maxTags} />
              ))}
              
              <h2 className="font-semibold mb-4 mt-8">With Div Element</h2>
              {mockFiles.map(file => (
                <TestRowWithDiv key={`div-${file.id}`} file={file} maxTags={maxTags} />
              ))}
            </div>
          </div>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        <ResizablePanel defaultSize={70}>
          <div className="h-full p-4 bg-muted/20">
            <h2 className="font-semibold mb-4">Expected Behavior</h2>
            <ul className="space-y-2 text-sm">
              <li>• Tags should NEVER disappear first</li>
              <li>• Filename should truncate with "..." when space is limited</li>
              <li>• Tags should "push" the filename to truncate</li>
              <li>• Resize the left panel to test different widths</li>
              <li>• Compare Button vs Div behavior</li>
            </ul>
            
            <div className="mt-8">
              <h3 className="font-semibold mb-2">Current Panel Breakpoints</h3>
              <div className="text-sm space-y-1">
                <div className={`p-2 rounded ${panelSize > 40 ? 'bg-green-100' : 'bg-gray-100'}`}>
                  Wide (&gt;40%): 3 tags
                </div>
                <div className={`p-2 rounded ${panelSize > 25 && panelSize <= 40 ? 'bg-yellow-100' : 'bg-gray-100'}`}>
                  Medium (25-40%): 2 tags  
                </div>
                <div className={`p-2 rounded ${panelSize <= 25 ? 'bg-red-100' : 'bg-gray-100'}`}>
                  Narrow (≤25%): 1 tag
                </div>
              </div>
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}