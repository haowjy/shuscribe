"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { createPortal } from "react-dom";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X, Plus, File, Folder } from "lucide-react";
import { TreeItem, Tag, isFile, isFolder } from "@/data/file-tree";
import { UpdateDocumentRequest } from "@/types/api";

interface MetadataEditorProps {
  item: TreeItem;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updates: UpdateDocumentRequest) => Promise<void>;
}

interface EditableMetadata {
  title: string;
  path: string;
  tags: Tag[];
  description?: string;
  // Using existing fields we have available
  status: 'unlocked' | 'locked'; // Based on is_locked field
  // Future fields (when API supports them)
  // publicationStatus: 'draft' | 'published' | 'archived';
  // contentType: string;
}

export function MetadataEditor({ item, isOpen, onClose, onSave }: MetadataEditorProps) {
  const [metadata, setMetadata] = useState<EditableMetadata>({
    title: '',
    path: '',
    tags: [],
    description: '',
    status: 'unlocked',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [newTagName, setNewTagName] = useState('');

  // Initialize metadata when item changes
  useEffect(() => {
    if (item) {
      setMetadata({
        title: item.name,
        path: `/${item.name}`, // TODO: Use getItemPath() from FileTreeService for proper hierarchical path
        tags: item.tags || [],
        description: '', // TODO: Add description field to TreeItem
        status: 'unlocked', // TODO: Map from item.is_locked when available
      });
    }
  }, [item]);

  const handleSave = async () => {
    if (!isFile(item)) {
      // For folders, we might want to handle differently in the future
      onClose();
      return;
    }

    setIsSaving(true);
    try {
      const updates: UpdateDocumentRequest = {
        title: metadata.title,
        tags: metadata.tags.map(tag => tag.name).filter(Boolean),
        // content: undefined, // Don't update content in metadata editor
      };

      await onSave(updates);
      onClose();
    } catch (error) {
      console.error('Failed to save metadata:', error);
      // TODO: Show error toast
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddTag = () => {
    if (!newTagName.trim()) return;
    
    const newTag: Tag = {
      id: `temp-${Date.now()}`,
      name: newTagName.trim(),
      color: undefined,
      icon: undefined,
    };

    setMetadata(prev => ({
      ...prev,
      tags: [...prev.tags, newTag]
    }));
    setNewTagName('');
  };

  const handleRemoveTag = (tagToRemove: Tag) => {
    setMetadata(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag.id !== tagToRemove.id)
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAddTag();
    }
  };

  if (!isOpen) return null;

  const modalContent = (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg border w-full max-w-[500px] mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            {isFolder(item) ? (
              <Folder className="h-4 w-4 text-blue-500" />
            ) : (
              <File className="h-4 w-4 text-muted-foreground" />
            )}
            Edit Metadata
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Edit the metadata for &quot;{item.name}&quot;
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={metadata.title}
              onChange={(e) => setMetadata(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter title..."
            />
          </div>

          {/* Path */}
          <div className="space-y-2">
            <Label htmlFor="path">Path</Label>
            <Input
              id="path"
              value={metadata.path}
              onChange={(e) => setMetadata(prev => ({ ...prev, path: e.target.value }))}
              placeholder="Enter path..."
            />
          </div>

          {/* Status (using available fields) */}
          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select
              value={metadata.status}
              onValueChange={(value: 'unlocked' | 'locked') => 
                setMetadata(prev => ({ ...prev, status: value }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="unlocked">Unlocked</SelectItem>
                <SelectItem value="locked">Locked</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={metadata.description}
              onChange={(e) => setMetadata(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter description..."
              rows={3}
            />
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label>Tags</Label>
            <div className="flex flex-wrap gap-1 mb-2">
              {metadata.tags.map((tag) => (
                <Badge
                  key={tag.id}
                  variant="secondary"
                  className="text-xs px-2 py-1 gap-1"
                  style={tag.color ? { backgroundColor: tag.color, color: '#fff' } : undefined}
                >
                  {tag.name}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="text-xs hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Add new tag..."
                className="flex-1"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddTag}
                disabled={!newTagName.trim()}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Future fields - commented out until API supports them */}
          {/*
          <div className="space-y-2">
            <Label htmlFor="publication-status">Publication Status</Label>
            <Select
              value={metadata.publicationStatus}
              onValueChange={(value) => 
                setMetadata(prev => ({ ...prev, publicationStatus: value }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select publication status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="published">Published</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
          </div>
          */}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={isSaving}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>
    </div>
  );

  return typeof window !== 'undefined' ? createPortal(modalContent, document.body) : null;
}