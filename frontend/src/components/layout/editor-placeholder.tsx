"use client";

import { useState } from "react";
import { X, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

interface EditorTab {
  id: string;
  name: string;
  content: string;
  isActive: boolean;
}

const mockTabs: EditorTab[] = [
  {
    id: "1",
    name: "elara.md",
    content: `# Elara Brightflame

## Character Profile
- **Age**: 23
- **Magic**: Fire elemental
- **Background**: Noble-born, but haunted by trauma

## Personality
Elara is cautious about using her powers after accidentally burning down her childhood home. She's been suppressing her abilities for three years, but recent events may force her to embrace them again.

## Relationships
- **@characters/protagonists/marcus**: Her mentor and guide
- **@locations/capital-city**: Where she currently lives in exile`,
    isActive: true,
  },
  {
    id: "2",
    name: "chapter-01.md",
    content: `# Chapter 1: Awakening

The morning mist clung to the cobblestones of @locations/capital-city as @characters/protagonists/elara made her way through the narrow alleys. She had been hiding for three years, but today everything would change.

Her fingers trembled as she felt the familiar warmth building in her chest. The @fire-magic that had once consumed her childhood home was stirring again, and this time she couldn't run from it.`,
    isActive: false,
  },
];

export function EditorPlaceholder() {
  const [tabs, setTabs] = useState(mockTabs);
  const [activeTabId, setActiveTabId] = useState("1");

  const activeTab = tabs.find(tab => tab.id === activeTabId);

  const closeTab = (tabId: string) => {
    const newTabs = tabs.filter(tab => tab.id !== tabId);
    setTabs(newTabs);
    if (tabId === activeTabId && newTabs.length > 0) {
      setActiveTabId(newTabs[0].id);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Tab Bar */}
      <div className="flex items-center border-b bg-secondary/20">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm border-r cursor-pointer group",
              activeTabId === tab.id 
                ? "bg-background text-foreground border-b-2 border-b-primary" 
                : "hover:bg-secondary/50 text-muted-foreground"
            )}
            onClick={() => setActiveTabId(tab.id)}
          >
            <span>{tab.name}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                closeTab(tab.id);
              }}
              className="opacity-0 group-hover:opacity-100 hover:bg-accent rounded p-0.5 transition-opacity"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        ))}
        <button className="p-2 hover:bg-accent text-muted-foreground">
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-auto">
        {activeTab ? (
          <div className="p-4 h-full">
            <div className="font-mono text-sm whitespace-pre-wrap leading-relaxed">
              {activeTab.content.split(/(@[a-zA-Z0-9-_/]+)/).map((part, index) => {
                if (part.startsWith('@')) {
                  return (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-1 rounded cursor-pointer hover:bg-blue-200"
                    >
                      {part}
                    </span>
                  );
                }
                return part;
              })}
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            No document open
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="h-6 bg-secondary/20 border-t flex items-center justify-between px-4 text-xs text-muted-foreground">
        <span>
          {activeTab ? `${activeTab.content.split(' ').length} words` : 'No document'}
        </span>
        <span>Auto-saved</span>
      </div>
    </div>
  );
}