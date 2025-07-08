"use client";

import { useState } from "react";
import { X, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EditorTab, mockTabs } from "@/data/editor-tabs";
import { cn } from "@/lib/utils";

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
              "flex items-center gap-2 px-3 py-2 text-sm border-r cursor-pointer group relative",
              activeTabId === tab.id 
                ? "bg-background text-foreground border-b-2 border-b-primary" 
                : "hover:bg-secondary/50 text-muted-foreground"
            )}
            onClick={() => setActiveTabId(tab.id)}
          >
            <span>{tab.name}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                closeTab(tab.id);
              }}
              className="opacity-0 group-hover:opacity-100 h-auto p-0.5 transition-opacity"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        ))}
        <Button variant="ghost" size="sm" className="p-2 text-muted-foreground">
          <Plus className="h-4 w-4" />
        </Button>
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
                      className="bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer px-1 py-0.5 rounded text-xs font-medium inline"
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