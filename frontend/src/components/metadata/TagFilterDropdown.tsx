"use client";

import React, { useState, useMemo } from 'react';
import { Filter, Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import { ProjectTag } from '@/types/tags';

interface TagFilterDropdownProps {
  allTags: ProjectTag[];
  activeFilters: string[];
  onFiltersChange: (filters: string[]) => void;
}

export function TagFilterDropdown({ 
  allTags, 
  activeFilters, 
  onFiltersChange 
}: TagFilterDropdownProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const filteredTags = useMemo(() => {
    if (!searchQuery.trim()) return allTags;
    
    return allTags.filter(tag =>
      tag.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [allTags, searchQuery]);

  const toggleFilter = (tagName: string, checked: boolean) => {
    if (checked) {
      onFiltersChange([...activeFilters, tagName]);
    } else {
      onFiltersChange(activeFilters.filter(filter => filter !== tagName));
    }
  };

  const clearFilters = () => {
    onFiltersChange([]);
    setSearchQuery('');
  };

  const clearSearch = () => {
    setSearchQuery('');
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 gap-2">
          <Filter className="h-3 w-3" />
          <span className="hidden sm:inline">Tags</span>
          {activeFilters.length > 0 && (
            <Badge variant="secondary" className="h-4 w-4 p-0 text-xs rounded-full">
              {activeFilters.length}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-72 p-0">
        <div className="p-4 space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <span className="font-medium text-sm">Filter by Tags</span>
            {activeFilters.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="h-6 text-xs px-2"
              >
                Clear All
              </Button>
            )}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-2 top-2 h-3 w-3 text-muted-foreground" />
            <Input
              placeholder="Search tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 pl-7 pr-7 text-sm"
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearSearch}
                className="absolute right-1 top-1 h-6 w-6 p-0"
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>

          {/* Active Filters */}
          {activeFilters.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs text-muted-foreground">Active Filters:</span>
              <div className="flex flex-wrap gap-1">
                {activeFilters.map((filter, index) => (
                  <Badge
                    key={`active-filter-${index}-${filter}`}
                    variant="secondary"
                    className="text-xs px-2 py-1 gap-1"
                  >
                    {filter}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleFilter(filter, false)}
                      className="h-3 w-3 p-0 hover:bg-destructive hover:text-destructive-foreground"
                    >
                      <X className="h-2 w-2" />
                    </Button>
                  </Badge>
                ))}
              </div>
              <Separator />
            </div>
          )}

          {/* Tag List */}
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">
              Available Tags ({filteredTags.length}):
            </span>
            
            <ScrollArea className="h-48">
              <div className="space-y-1 pr-3">
                {filteredTags.length === 0 ? (
                  <div className="text-xs text-muted-foreground py-4 text-center">
                    {searchQuery ? 'No tags found' : 'No tags available'}
                  </div>
                ) : (
                  filteredTags.map((tag, index) => (
                    <label
                      key={tag.id || `tag-${index}-${tag.name}`}
                      className="flex items-center gap-3 px-2 py-1.5 hover:bg-accent rounded-sm cursor-pointer"
                    >
                      <Checkbox
                        checked={activeFilters.includes(tag.name)}
                        onCheckedChange={(checked) => 
                          toggleFilter(tag.name, checked as boolean)
                        }
                      />
                      
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <Badge
                          variant="secondary"
                          className="text-xs gap-1"
                          style={{ 
                            backgroundColor: tag.color || undefined,
                            color: tag.color ? '#fff' : undefined 
                          }}
                        >
                          {tag.icon && <span>{tag.icon}</span>}
                          {tag.name}
                        </Badge>
                        
                        <span className="text-xs text-muted-foreground ml-auto">
                          ({tag.usage_count})
                        </span>
                      </div>
                    </label>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>

          {/* Footer */}
          {filteredTags.length > 0 && (
            <div className="text-xs text-muted-foreground">
              {activeFilters.length > 0 
                ? `${activeFilters.length} filter${activeFilters.length === 1 ? '' : 's'} applied`
                : 'Select tags to filter files'
              }
            </div>
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}