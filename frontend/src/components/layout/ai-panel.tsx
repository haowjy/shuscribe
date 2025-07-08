"use client";

import { useState } from "react";
import { Bot, ChevronDown, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

const aiModes = [
  { value: "writing", label: "Chapter Writing", icon: "✍️" },
  { value: "character", label: "Character Development", icon: "👥" },
  { value: "worldbuilding", label: "World Building", icon: "🌍" },
  { value: "plot", label: "Plot Planning", icon: "📋" },
  { value: "dialogue", label: "Dialogue Polish", icon: "💬" },
];

const mockContext = [
  { type: "character", name: "elara", description: "Fire magic user, trauma survivor" },
  { type: "location", name: "capital-city", description: "Urban setting, political intrigue" },
  { type: "tag", name: "fire-magic", description: "Elemental magic system" },
];

export function AiPanel() {
  const [selectedMode, setSelectedMode] = useState("writing");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const currentMode = aiModes.find(mode => mode.value === selectedMode);

  return (
    <div className="h-full flex flex-col">
      {/* Mode Selector */}
      <div className="relative">
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="w-full flex items-center justify-between p-3 bg-secondary/30 hover:bg-secondary/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <span className="text-sm">{currentMode?.icon}</span>
            <span className="text-sm font-medium">{currentMode?.label}</span>
          </div>
          <ChevronDown className={cn(
            "h-4 w-4 transition-transform",
            isDropdownOpen && "rotate-180"
          )} />
        </button>
        
        {isDropdownOpen && (
          <div className="absolute top-full left-0 right-0 bg-background border border-border rounded-md shadow-lg z-10">
            {aiModes.map((mode) => (
              <button
                key={mode.value}
                onClick={() => {
                  setSelectedMode(mode.value);
                  setIsDropdownOpen(false);
                }}
                className={cn(
                  "w-full flex items-center gap-2 p-3 text-left hover:bg-secondary/50 transition-colors",
                  selectedMode === mode.value && "bg-secondary/30"
                )}
              >
                <span className="text-sm">{mode.icon}</span>
                <span className="text-sm">{mode.label}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Context Section */}
      <div className="p-3 border-b">
        <div className="flex items-center gap-2 mb-2">
          <Lightbulb className="h-4 w-4 text-yellow-500" />
          <span className="text-sm font-medium">Context</span>
        </div>
        <div className="space-y-1">
          {mockContext.map((item, index) => (
            <div key={index} className="text-xs bg-secondary/30 p-2 rounded">
              <div className="font-medium text-foreground">
                {item.type === "character" && "👤"}
                {item.type === "location" && "📍"}
                {item.type === "tag" && "🏷️"}
                {" " + item.name}
              </div>
              <div className="text-muted-foreground mt-1">{item.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-3 overflow-auto">
          <div className="space-y-3">
            <div className="flex items-start gap-2">
              <Bot className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="text-sm bg-secondary/30 p-2 rounded">
                <p className="text-foreground">
                  I'm ready to help with your {currentMode?.label.toLowerCase()}! 
                  Based on your current context, I can see you're working with Elara, 
                  a fire magic user in the capital city.
                </p>
                <p className="text-muted-foreground mt-1 text-xs">
                  ✨ AI features coming soon
                </p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 p-3 rounded text-sm">
              <div className="font-medium text-blue-900 mb-1">Sample AI Suggestions:</div>
              <ul className="text-blue-700 space-y-1 text-xs">
                <li>• How can Elara overcome her fear of fire magic?</li>
                <li>• What political tensions exist in the capital city?</li>
                <li>• Suggest a scene where Elara confronts her trauma</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Chat Input */}
        <div className="p-3 border-t">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask about your story..."
              className="flex-1 px-3 py-2 text-sm bg-secondary/30 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              disabled
            />
            <button
              className="px-3 py-2 bg-primary text-primary-foreground rounded-md text-sm opacity-50 cursor-not-allowed"
              disabled
            >
              Send
            </button>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            AI chat coming in future updates
          </div>
        </div>
      </div>
    </div>
  );
}