"use client";

import React, { useState, useCallback } from 'react';
import { Plus, X, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { TreeItem } from '@/types/api';
import { ProjectTag, CreateTagRequest } from '@/types/tags';

interface QuickTagEditorProps {
  item: TreeItem;
  onSave: (metadata: { tag_ids: string[] }) => Promise<void>;
  isSaving?: boolean;
  availableTags?: ProjectTag[];
  onCreateTag?: (tag: CreateTagRequest) => Promise<ProjectTag>;
}

export function QuickTagEditor({ 
  item, 
  onSave, 
  isSaving = false,
  availableTags = [],
  onCreateTag
}: QuickTagEditorProps) {
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>(item.tags?.map(tag => typeof tag === 'string' ? tag : tag.id) || []);
  const [newTagName, setNewTagName] = useState('');
  const [suggestions, setSuggestions] = useState<ProjectTag[]>([]);
  
  // Get selected tags as objects
  const selectedTags = availableTags.filter(tag => selectedTagIds.includes(tag.id));

  const handleNewTagChange = useCallback((value: string) => {
    setNewTagName(value);
    
    if (value.trim()) {
      // Filter suggestions based on input and exclude already selected tags
      const filtered = availableTags
        .filter(tag => 
          tag.name.toLowerCase().includes(value.toLowerCase()) &&
          !selectedTagIds.includes(tag.id) &&
          !tag.is_archived
        )
        .slice(0, 5);
      setSuggestions(filtered);
    } else {
      setSuggestions([]);
    }
  }, [availableTags, selectedTagIds]);

  const addExistingTag = useCallback((tag: ProjectTag) => {
    if (!selectedTagIds.includes(tag.id)) {
      setSelectedTagIds(prev => [...prev, tag.id]);
      setNewTagName('');
      setSuggestions([]);
    }
  }, [selectedTagIds]);

  const createAndAddTag = useCallback(async () => {
    const trimmed = newTagName.trim();
    if (!trimmed || !onCreateTag) return;
    
    try {
      const newTag = await onCreateTag({ name: trimmed });
      setSelectedTagIds(prev => [...prev, newTag.id]);
      setNewTagName('');
      setSuggestions([]);
    } catch (error) {
      console.error('Failed to create tag:', error);
    }
  }, [newTagName, onCreateTag]);

  const removeTag = useCallback((tagId: string) => {
    setSelectedTagIds(prev => prev.filter(id => id !== tagId));
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      // Try to find exact match first
      const exactMatch = availableTags.find(tag => 
        tag.name.toLowerCase() === newTagName.toLowerCase().trim()
      );
      if (exactMatch) {
        addExistingTag(exactMatch);
      } else {
        createAndAddTag();
      }
    } else if (e.key === 'Escape') {
      setNewTagName('');
      setSuggestions([]);
    }
  }, [newTagName, availableTags, addExistingTag, createAndAddTag]);

  const handleSave = useCallback(async () => {
    await onSave({ tag_ids: selectedTagIds });
  }, [selectedTagIds, onSave]);

  const hasChanges = JSON.stringify(selectedTagIds.sort()) !== JSON.stringify((item.tags?.map(t => typeof t === 'string' ? t : t.id) || []).sort());

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium flex items-center gap-2">
          <Tag className="h-3 w-3" />
          Tags
        </Label>
        <Badge variant="outline" className="text-xs">
          {selectedTags.length} tags
        </Badge>
      </div>

      {/* Tag Input */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <Input
            placeholder="Add tag..."
            value={newTagName}
            onChange={(e) => handleNewTagChange(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 h-8 text-sm"
          />
          <Button 
            size="sm" 
            onClick={createAndAddTag}
            disabled={!newTagName.trim()}
            className="h-8 px-3"
          >
            <Plus className="h-3 w-3" />
          </Button>
        </div>

        {/* Tag Suggestions */}
        {suggestions.length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Suggestions:</span>
            <div className="flex flex-wrap gap-1">
              {suggestions.map((suggestion) => (
                <Button
                  key={suggestion.id}
                  variant="outline"
                  size="sm"
                  onClick={() => addExistingTag(suggestion)}
                  className="h-6 text-xs px-2 gap-1 hover:bg-secondary"
                >
                  {suggestion.icon && <span>{suggestion.icon}</span>}
                  {suggestion.name}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Current Tags */}
      <div className="space-y-2">
        <Label className="text-xs text-muted-foreground">Current Tags:</Label>
        {selectedTags.length > 0 ? (
          <div className="flex flex-wrap gap-1">
            {selectedTags.map((tag) => (
              <Badge
                key={tag.id}
                variant="secondary"
                className="text-xs px-2 py-1 gap-1 cursor-default"
                style={{ 
                  backgroundColor: tag.color || undefined,
                  color: tag.color ? '#fff' : undefined 
                }}
              >
                {tag.icon && <span>{tag.icon}</span>}
                {tag.name}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeTag(tag.id)}
                  className="h-3 w-3 p-0 hover:bg-destructive hover:text-destructive-foreground"
                >
                  <X className="h-2 w-2" />
                </Button>
              </Badge>
            ))}
          </div>
        ) : (
          <div className="text-xs text-muted-foreground py-2">
            No tags added yet. Add some tags to organize your content.
          </div>
        )}
      </div>

      {/* Save Button */}
      {hasChanges && (
        <div className="flex justify-end pt-2">
          <Button
            size="sm"
            onClick={handleSave}
            disabled={isSaving}
            className="h-8"
          >
            {isSaving ? 'Saving...' : 'Save Tags'}
          </Button>
        </div>
      )}
    </div>
  );
}