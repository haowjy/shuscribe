"use client";

import { useState } from "react";
import { Bot, Lightbulb, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { aiModes, mockContext, getAiModeById } from "@/data/ai-modes";
import { cn } from "@/lib/utils";

export function AiPanel() {
  const [selectedMode, setSelectedMode] = useState("writing");

  const currentMode = getAiModeById(selectedMode);

  return (
    <div className="h-full flex flex-col">
      {/* Mode Selector */}
      <div className="p-3 bg-secondary/30">
        <Select value={selectedMode} onValueChange={setSelectedMode}>
          <SelectTrigger className="w-full">
            <SelectValue>
              <div className="flex items-center gap-2">
                <span className="text-sm">{currentMode?.icon}</span>
                <span className="text-sm font-medium">{currentMode?.label}</span>
              </div>
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {aiModes.map((mode) => (
              <SelectItem key={mode.value} value={mode.value}>
                <div className="flex items-center gap-2">
                  <span className="text-sm">{mode.icon}</span>
                  <span className="text-sm">{mode.label}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Context Section */}
      <Card className="border-0 border-b rounded-none">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Lightbulb className="h-4 w-4 text-yellow-500" />
            Context
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            {mockContext.map((item, index) => (
              <Badge key={index} variant="secondary" className="w-full justify-start p-2 h-auto">
                <div className="flex flex-col items-start w-full">
                  <div className="font-medium text-foreground text-xs">
                    {item.type === "character" && "👤"}
                    {item.type === "location" && "📍"}
                    {item.type === "tag" && "🏷️"}
                    {" " + item.name}
                  </div>
                  <div className="text-muted-foreground text-xs mt-1">{item.description}</div>
                </div>
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <CardContent className="flex-1 overflow-auto">
          <div className="space-y-3">
            <Card>
              <CardContent className="p-3">
                <div className="flex items-start gap-2">
                  <Bot className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div className="text-sm">
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
              </CardContent>
            </Card>
            
            <Card className="bg-blue-50 border border-blue-200">
              <CardContent className="p-3">
                <div className="font-medium text-blue-900 mb-1 text-sm">Sample AI Suggestions:</div>
                <ul className="text-blue-700 space-y-1 text-xs">
                  <li>• How can Elara overcome her fear of fire magic?</li>
                  <li>• What political tensions exist in the capital city?</li>
                  <li>• Suggest a scene where Elara confronts her trauma</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </CardContent>

        {/* Chat Input */}
        <Card className="border-0 border-t rounded-none">
          <CardContent className="p-3">
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="Ask about your story..."
                disabled
                className="flex-1"
              />
              <Button disabled size="sm" className="gap-2">
                <Send className="h-4 w-4" />
                Send
              </Button>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              AI chat coming in future updates
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}