"use client";

import React, { useState, useCallback } from 'react';
import { Palette, FolderOpen, FileText, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { TreeItem } from '@/types/api';

interface MetadataFormProps {
  item: TreeItem;
  onSave: (metadata: any) => Promise<void>;
  isSaving?: boolean;
}

interface FormData {
  name: string;
  description: string;
  icon: string;
  color: string;
  priority: string;
  category: string;
}

const PRIORITY_OPTIONS = [
  { value: '', label: 'None', icon: '⚪', color: 'text-muted-foreground' },
  { value: 'low', label: 'Low', icon: '🟢', color: 'text-green-600' },
  { value: 'medium', label: 'Medium', icon: '🟡', color: 'text-yellow-600' },
  { value: 'high', label: 'High', icon: '🔴', color: 'text-red-600' },
];

const ICON_OPTIONS = [
  { value: '', label: 'Default', icon: '📄' },
  { value: 'character', label: 'Character', icon: '👤' },
  { value: 'location', label: 'Location', icon: '📍' },
  { value: 'plot', label: 'Plot', icon: '📚' },
  { value: 'notes', label: 'Notes', icon: '📝' },
  { value: 'research', label: 'Research', icon: '🔍' },
  { value: 'ideas', label: 'Ideas', icon: '💡' },
  { value: 'drafts', label: 'Drafts', icon: '✏️' },
];

const COLOR_OPTIONS = [
  { value: '', label: 'Default', color: 'transparent' },
  { value: '#ef4444', label: 'Red', color: '#ef4444' },
  { value: '#f97316', label: 'Orange', color: '#f97316' },
  { value: '#eab308', label: 'Yellow', color: '#eab308' },
  { value: '#22c55e', label: 'Green', color: '#22c55e' },
  { value: '#3b82f6', label: 'Blue', color: '#3b82f6' },
  { value: '#8b5cf6', label: 'Purple', color: '#8b5cf6' },
  { value: '#ec4899', label: 'Pink', color: '#ec4899' },
];

export function MetadataForm({ item, onSave, isSaving = false }: MetadataFormProps) {
  const [formData, setFormData] = useState<FormData>({
    name: item.name,
    description: '',
    icon: item.icon || '',
    color: '',
    priority: '',
    category: '',
  });

  const updateFormData = useCallback((updates: Partial<FormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  }, []);

  const handleSave = useCallback(async () => {
    const metadata = {
      name: formData.name,
      description: formData.description || undefined,
      icon: formData.icon || undefined,
      color: formData.color || undefined,
      priority: formData.priority || undefined,
      category: formData.category || undefined,
    };
    
    await onSave(metadata);
  }, [formData, onSave]);

  const hasChanges = 
    formData.name !== item.name ||
    formData.description !== '' ||
    formData.icon !== (item.icon || '') ||
    formData.color !== '' ||
    formData.priority !== '' ||
    formData.category !== '';

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <div className="space-y-4">
        <Label className="text-sm font-medium flex items-center gap-2">
          {item.type === 'file' ? (
            <FileText className="h-3 w-3" />
          ) : (
            <FolderOpen className="h-3 w-3" />
          )}
          Basic Information
        </Label>

        <div className="space-y-3">
          <div className="space-y-1">
            <Label htmlFor="name" className="text-xs">Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => updateFormData({ name: e.target.value })}
              className="h-8 text-sm"
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="description" className="text-xs">Description</Label>
            <Textarea
              id="description"
              placeholder="Optional description..."
              value={formData.description}
              onChange={(e) => updateFormData({ description: e.target.value })}
              className="min-h-[60px] text-sm resize-none"
            />
          </div>
        </div>
      </div>

      {/* Visual Properties */}
      <div className="space-y-4">
        <Label className="text-sm font-medium flex items-center gap-2">
          <Palette className="h-3 w-3" />
          Visual Properties
        </Label>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label htmlFor="icon" className="text-xs">Icon</Label>
            <Select value={formData.icon} onValueChange={(value) => updateFormData({ icon: value })}>
              <SelectTrigger className="h-8 text-sm">
                <SelectValue placeholder="Choose icon..." />
              </SelectTrigger>
              <SelectContent>
                {ICON_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <span className="flex items-center gap-2">
                      <span>{option.icon}</span>
                      <span>{option.label}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="color" className="text-xs">Color</Label>
            <Select value={formData.color} onValueChange={(value) => updateFormData({ color: value })}>
              <SelectTrigger className="h-8 text-sm">
                <SelectValue placeholder="Choose color..." />
              </SelectTrigger>
              <SelectContent>
                {COLOR_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <span className="flex items-center gap-2">
                      <span 
                        className="w-3 h-3 rounded-full border border-border"
                        style={{ backgroundColor: option.color }}
                      />
                      <span>{option.label}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Workflow Properties */}
      <div className="space-y-4">
        <Label className="text-sm font-medium flex items-center gap-2">
          <Star className="h-3 w-3" />
          Workflow
        </Label>

        <div className="grid grid-cols-1 gap-3">
          <div className="space-y-1">
            <Label htmlFor="priority" className="text-xs">Priority</Label>
            <Select value={formData.priority} onValueChange={(value) => updateFormData({ priority: value })}>
              <SelectTrigger className="h-8 text-sm">
                <SelectValue placeholder="Set priority..." />
              </SelectTrigger>
              <SelectContent>
                {PRIORITY_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <span className={`flex items-center gap-2 ${option.color}`}>
                      <span>{option.icon}</span>
                      <span>{option.label}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="category" className="text-xs">Category</Label>
            <Input
              id="category"
              placeholder="e.g., character, location, plot..."
              value={formData.category}
              onChange={(e) => updateFormData({ category: e.target.value })}
              className="h-8 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Preview */}
      {(formData.color || formData.icon || formData.priority) && (
        <div className="space-y-2 p-3 bg-muted/50 rounded-md">
          <Label className="text-xs text-muted-foreground">Preview:</Label>
          <div className="flex items-center gap-2">
            <span>{ICON_OPTIONS.find(opt => opt.value === formData.icon)?.icon || '📄'}</span>
            <span className="text-sm">{formData.name}</span>
            {formData.priority && (
              <Badge 
                variant="outline" 
                className="text-xs h-5"
              >
                {PRIORITY_OPTIONS.find(opt => opt.value === formData.priority)?.icon}
                {PRIORITY_OPTIONS.find(opt => opt.value === formData.priority)?.label}
              </Badge>
            )}
          </div>
        </div>
      )}

      {/* Save Button */}
      {hasChanges && (
        <div className="flex justify-end pt-2">
          <Button
            size="sm"
            onClick={handleSave}
            disabled={isSaving}
            className="h-8"
          >
            {isSaving ? 'Saving...' : 'Save Properties'}
          </Button>
        </div>
      )}
    </div>
  );
}