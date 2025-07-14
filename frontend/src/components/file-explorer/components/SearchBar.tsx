"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Plus, Filter, ChevronDown, ChevronUp } from "lucide-react";
import { Tag } from "@/data/file-tree";
import { FileSearchState } from "../types/file-explorer";

interface SearchBarProps {
  searchState: FileSearchState;
  allTags: Tag[];
  onSearchStateChange: (updates: Partial<FileSearchState>) => void;
}

export function SearchBar({ searchState, allTags, onSearchStateChange }: SearchBarProps) {
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  return (
    <div className="space-y-2 p-2 border-b">
      {/* Header with title and actions */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">
          Project Files
        </span>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="p-1 h-auto"
            title="Toggle advanced filters"
          >
            <Filter className="h-3 w-3" />
            {showAdvancedFilters ? (
              <ChevronUp className="h-3 w-3 ml-1" />
            ) : (
              <ChevronDown className="h-3 w-3 ml-1" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              // TODO: Implement new file creation
              console.log('Create new file');
            }}
            className="p-1 h-auto"
            title="Create new file"
          >
            <Plus className="h-3 w-3" />
          </Button>
        </div>
      </div>
      
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-2 top-2 h-3 w-3 text-muted-foreground" />
        <Input
          placeholder="Search files..."
          value={searchState.query}
          onChange={(e) => onSearchStateChange({ query: e.target.value })}
          className="h-7 pl-7 text-sm"
        />
      </div>
      
      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <div className="space-y-3 pt-2 border-t">
          <div className="text-xs font-medium text-muted-foreground">Advanced Filters</div>
          
          {/* Simple file/folder filter */}
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">Show</label>
            <Select
              value={searchState.statusFilter}
              onValueChange={(value: 'all' | 'files' | 'folders') => onSearchStateChange({ statusFilter: value })}
            >
              <SelectTrigger className="h-6 text-xs">
                <SelectValue placeholder="All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Items</SelectItem>
                <SelectItem value="files">Files Only</SelectItem>
                <SelectItem value="folders">Folders Only</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tag Filter Selection */}
          {allTags.length > 0 && (
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Tags</label>
              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                {allTags.slice(0, 10).map((tag) => (
                  <Badge
                    key={tag.id}
                    variant={searchState.tagFilters.includes(tag.name) ? "default" : "outline"}
                    className="text-xs cursor-pointer hover:bg-accent"
                    onClick={() => {
                      const isSelected = searchState.tagFilters.includes(tag.name);
                      const newFilters = isSelected
                        ? searchState.tagFilters.filter(f => f !== tag.name)
                        : [...searchState.tagFilters, tag.name];
                      onSearchStateChange({ tagFilters: newFilters });
                    }}
                  >
                    {tag.name}
                  </Badge>
                ))}
                {allTags.length > 10 && (
                  <span className="text-xs text-muted-foreground">+{allTags.length - 10} more</span>
                )}
              </div>
            </div>
          )}

          {/* Clear Filters Button */}
          <Button
            variant="outline"
            size="sm"
            className="h-6 text-xs"
            onClick={() => {
              onSearchStateChange({
                query: '',
                tagFilters: [],
                statusFilter: 'all',
                contentTypeFilter: []
              });
            }}
          >
            Clear All Filters
          </Button>
        </div>
      )}

      {/* Active filters display */}
      {(searchState.query || searchState.tagFilters.length > 0 || searchState.statusFilter !== 'all') && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-muted-foreground">Filtered:</span>
          {searchState.query && (
            <Badge variant="outline" className="text-xs">
              &quot;{searchState.query}&quot;
            </Badge>
          )}
          {searchState.statusFilter !== 'all' && (
            <Badge variant="outline" className="text-xs">
              {searchState.statusFilter}
            </Badge>
          )}
          {searchState.tagFilters.map((filter, index) => (
            <Badge 
              key={`tag-${index}`} 
              variant="secondary" 
              className="text-xs cursor-pointer"
              onClick={() => {
                const newFilters = searchState.tagFilters.filter(f => f !== filter);
                onSearchStateChange({ tagFilters: newFilters });
              }}
            >
              {filter} ×
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}