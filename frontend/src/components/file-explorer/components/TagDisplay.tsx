"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { TagDisplayProps } from "../types/file-explorer";
import { DynamicIcon } from "lucide-react/dynamic";

export function TagDisplay({ 
  tags, 
  maxVisible = 3,
  onTagClick 
}: TagDisplayProps) {
  // Debug logging
  console.log('🏷️ [TagDisplay] Props received:', {
    tagsLength: tags?.length || 0,
    maxVisible,
    tagsArray: tags
  });

  if (!tags || tags.length === 0 || maxVisible === 0) {
    console.log('🏷️ [TagDisplay] Returning null - no tags or maxVisible=0');
    return null;
  }

  const visibleTags = tags.slice(0, maxVisible);
  const overflowCount = Math.max(0, tags.length - maxVisible);
  
  console.log('🏷️ [TagDisplay] Processing tags:', {
    totalTags: tags.length,
    maxVisible,
    visibleTagsCount: visibleTags.length,
    overflowCount,
    visibleTagNames: visibleTags.map(t => t.name)
  });

  return (
    <div className="flex gap-1 items-center flex-shrink-0">
        {visibleTags.map((tag) => (
          <Tooltip key={tag.id}>
            <TooltipTrigger asChild>
              <Badge
                variant="tag"
                className="text-xs px-1 py-0.5 h-auto cursor-pointer hover:bg-accent transition-colors"
                style={tag.color ? { backgroundColor: tag.color, color: '#fff' } : undefined}
                onClick={() => tag.name && onTagClick?.(tag.name)}
              >
                {tag.icon && <DynamicIcon name={tag.icon} className="w-3 h-3" />}
                {/* Only show icon, not name to save space */}
                {!tag.icon && tag.name && <span>{tag.name.charAt(0).toUpperCase()}</span>}
                {!tag.icon && !tag.name && <span>?</span>}
              </Badge>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              <div className="space-y-1">
                <div className="font-medium">{tag.name || 'Unknown tag'}</div>
                {tag.category && (
                  <div className="text-muted-foreground">Category: {tag.category}</div>
                )}
                <div className="text-muted-foreground">Click to filter by this tag</div>
              </div>
            </TooltipContent>
          </Tooltip>
        ))}
        
        {overflowCount > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge 
                variant="outline" 
                className="text-xs px-1 py-0.5 h-auto cursor-pointer hover:bg-accent transition-colors"
              >
                +{overflowCount}
              </Badge>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs max-w-48">
              <div className="space-y-1">
                <div className="font-medium">{overflowCount} more tag{overflowCount > 1 ? 's' : ''}</div>
                <div className="text-muted-foreground">
                  {tags.slice(maxVisible).map(t => t.name || 'Unknown').join(', ')}
                </div>
              </div>
            </TooltipContent>
          </Tooltip>
        )}
    </div>
  );
}