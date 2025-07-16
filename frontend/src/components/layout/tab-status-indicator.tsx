"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface TabStatusIndicatorProps {
  isDirty: boolean;
  hasDraft: boolean;
  isSaving?: boolean;
  lastSaved?: string;
  onClose: (e?: React.MouseEvent) => void;
  variant?: 'tab' | 'dropdown';
  className?: string;
}

export function TabStatusIndicator({ 
  isDirty, 
  hasDraft, 
  isSaving = false,
  lastSaved,
  onClose, 
  variant = 'tab',
  className 
}: TabStatusIndicatorProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  // Document is unsaved if:
  // 1. It's dirty (has unsaved changes), OR
  // 2. It has a draft but was never properly saved (no lastSaved)
  // BUT NOT if it was recently saved (has lastSaved) even if there's still a draft
  const isUnsaved = isDirty || (hasDraft && !lastSaved);

  if (variant === 'dropdown') {
    // For dropdown items - inline layout
    return (
      <div 
        className={cn("flex items-center justify-center w-5 h-5 relative", className)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Show X on hover (highest priority) */}
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onClose(e);
          }}
          onPointerDown={(e) => {
            e.stopPropagation();
          }}
          data-close-button="true"
          className={cn(
            "h-4 w-4 p-0 transition-opacity hover:bg-destructive/10 flex items-center justify-center absolute z-10",
            isHovered ? "opacity-100" : "opacity-0"
          )}
        >
          <X className="h-3 w-3" />
        </Button>
        
        {/* Show dot when unsaved (hidden on hover) */}
        {isUnsaved && (
          <span className={cn(
            "text-xs text-orange-500 transition-opacity absolute flex items-center justify-center h-4 w-4",
            isHovered ? "opacity-0 pointer-events-none" : "opacity-100"
          )}>
            •
          </span>
        )}
      </div>
    );
  }

  // Default tab variant - absolute positioned
  return (
    <div 
      className={cn("absolute right-1 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center", className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Show X on hover (highest priority) */}
      <Button
        variant="ghost"
        size="sm"
        onClick={(e) => {
          e.stopPropagation();
          onClose(e);
        }}
        onPointerDown={(e) => {
          e.stopPropagation();
        }}
        data-close-button="true"
        className={cn(
          "h-5 w-5 p-0 transition-opacity hover:bg-destructive/10 absolute inset-0 flex items-center justify-center z-10",
          isHovered ? "opacity-100" : "opacity-0"
        )}
      >
        <X className="h-3 w-3" />
      </Button>
      
      {/* Show dot when unsaved (hidden on hover) */}
      {isUnsaved && (
        <span className={cn(
          "text-xs text-orange-500 transition-opacity absolute inset-0 flex items-center justify-center",
          isHovered ? "opacity-0 pointer-events-none" : "opacity-100"
        )}>
          •
        </span>
      )}
    </div>
  );
}