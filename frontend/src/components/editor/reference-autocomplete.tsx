"use client";

import { useState, useCallback, useEffect, useImperativeHandle, forwardRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { File, Folder, User, MapPin, Hash } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ReferenceItem {
  id: string;
  name: string;
  type: "character" | "location" | "chapter" | "scene" | "note" | "document";
  path?: string;
  description?: string;
  tags?: string[];
}

interface ReferenceAutocompleteProps {
  items: ReferenceItem[];
  onSelect: (item: ReferenceItem) => void;
  onClose: () => void;
  position: { x: number; y: number };
  query: string;
  maxItems?: number;
  className?: string;
}

export interface ReferenceAutocompleteHandle {
  selectNext: () => void;
  selectPrevious: () => void;
  selectCurrent: () => void;
  close: () => void;
}

const getTypeIcon = (type: ReferenceItem["type"]) => {
  switch (type) {
    case "character":
      return <User className="h-4 w-4 text-blue-500" />;
    case "location":
      return <MapPin className="h-4 w-4 text-green-500" />;
    case "chapter":
      return <File className="h-4 w-4 text-purple-500" />;
    case "scene":
      return <Hash className="h-4 w-4 text-orange-500" />;
    case "note":
      return <File className="h-4 w-4 text-yellow-500" />;
    case "document":
      return <File className="h-4 w-4 text-gray-500" />;
    default:
      return <File className="h-4 w-4 text-gray-500" />;
  }
};

const getTypeColor = (type: ReferenceItem["type"]) => {
  switch (type) {
    case "character":
      return "bg-blue-100 text-blue-800 border-blue-200";
    case "location":
      return "bg-green-100 text-green-800 border-green-200";
    case "chapter":
      return "bg-purple-100 text-purple-800 border-purple-200";
    case "scene":
      return "bg-orange-100 text-orange-800 border-orange-200";
    case "note":
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    case "document":
      return "bg-gray-100 text-gray-800 border-gray-200";
    default:
      return "bg-gray-100 text-gray-800 border-gray-200";
  }
};

export const ReferenceAutocomplete = forwardRef<ReferenceAutocompleteHandle, ReferenceAutocompleteProps>(
  ({ items, onSelect, onClose, position, query, maxItems = 8, className }, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [filteredItems, setFilteredItems] = useState<ReferenceItem[]>([]);

    // Filter and sort items based on query
    useEffect(() => {
      if (!query.trim()) {
        setFilteredItems(items.slice(0, maxItems));
      } else {
        const searchQuery = query.toLowerCase().trim();
        const filtered = items
          .filter(item => {
            const nameMatch = item.name.toLowerCase().includes(searchQuery);
            const pathMatch = item.path?.toLowerCase().includes(searchQuery);
            const descMatch = item.description?.toLowerCase().includes(searchQuery);
            const tagMatch = item.tags?.some(tag => tag.toLowerCase().includes(searchQuery));
            return nameMatch || pathMatch || descMatch || tagMatch;
          })
          .sort((a, b) => {
            // Prioritize exact matches at start of name
            const aStartsWithQuery = a.name.toLowerCase().startsWith(searchQuery);
            const bStartsWithQuery = b.name.toLowerCase().startsWith(searchQuery);
            
            if (aStartsWithQuery && !bStartsWithQuery) return -1;
            if (!aStartsWithQuery && bStartsWithQuery) return 1;
            
            // Then by type priority (characters > locations > chapters > scenes > notes > documents)
            const typePriority = { character: 0, location: 1, chapter: 2, scene: 3, note: 4, document: 5 };
            const aPriority = typePriority[a.type] ?? 10;
            const bPriority = typePriority[b.type] ?? 10;
            
            if (aPriority !== bPriority) return aPriority - bPriority;
            
            // Finally by name alphabetically
            return a.name.localeCompare(b.name);
          })
          .slice(0, maxItems);
        
        setFilteredItems(filtered);
      }
      
      // Reset selection when items change
      setSelectedIndex(0);
    }, [items, query, maxItems]);

    // Handle keyboard navigation
    const selectNext = useCallback(() => {
      setSelectedIndex(prev => (prev + 1) % filteredItems.length);
    }, [filteredItems.length]);

    const selectPrevious = useCallback(() => {
      setSelectedIndex(prev => (prev - 1 + filteredItems.length) % filteredItems.length);
    }, [filteredItems.length]);

    const selectCurrent = useCallback(() => {
      const selectedItem = filteredItems[selectedIndex];
      if (selectedItem) {
        onSelect(selectedItem);
      }
    }, [filteredItems, selectedIndex, onSelect]);

    const close = useCallback(() => {
      onClose();
    }, [onClose]);

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      selectNext,
      selectPrevious,
      selectCurrent,
      close,
    }), [selectNext, selectPrevious, selectCurrent, close]);

    // Don't render if no items
    if (filteredItems.length === 0) {
      return null;
    }

    return (
      <Card
        className={cn(
          "absolute z-50 w-80 max-h-64 overflow-y-auto shadow-lg border bg-background/95 backdrop-blur-sm",
          className
        )}
        style={{
          left: position.x,
          top: position.y,
        }}
      >
        <div className="p-1">
          <div className="px-2 py-1 text-xs text-muted-foreground border-b mb-1">
            {query ? `Results for "@${query}"` : "Available references"}
          </div>
          
          {filteredItems.map((item, index) => (
            <Button
              key={item.id}
              variant="ghost"
              className={cn(
                "w-full justify-start p-2 h-auto text-left",
                index === selectedIndex && "bg-accent"
              )}
              onClick={() => onSelect(item)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="flex items-start gap-2 w-full">
                <div className="flex-shrink-0 mt-0.5">
                  {getTypeIcon(item.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium truncate">{item.name}</span>
                    <Badge 
                      variant="outline" 
                      className={cn("text-xs px-1.5 py-0 h-auto", getTypeColor(item.type))}
                    >
                      {item.type}
                    </Badge>
                  </div>
                  
                  {item.path && (
                    <div className="text-xs text-muted-foreground truncate">
                      {item.path}
                    </div>
                  )}
                  
                  {item.description && (
                    <div className="text-xs text-muted-foreground line-clamp-2 mt-1">
                      {item.description}
                    </div>
                  )}
                  
                  {item.tags && item.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {item.tags.slice(0, 3).map(tag => (
                        <Badge key={tag} variant="secondary" className="text-xs px-1 py-0 h-auto">
                          {tag}
                        </Badge>
                      ))}
                      {item.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs px-1 py-0 h-auto">
                          +{item.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Button>
          ))}
          
          {filteredItems.length === maxItems && items.length > maxItems && (
            <div className="px-2 py-1 text-xs text-muted-foreground text-center border-t mt-1">
              Showing {maxItems} of {items.length} results
            </div>
          )}
        </div>
      </Card>
    );
  }
);

ReferenceAutocomplete.displayName = "ReferenceAutocomplete";