"use client";

import React, { useState, useEffect } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { X, GripHorizontal, Settings, Tag, Palette, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { TreeItem } from '@/types/api';
import { QuickTagEditor } from './QuickTagEditor';
import { MetadataForm } from './MetadataForm';

interface DraggableMetadataPanelProps {
  item: TreeItem | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (metadata: any) => Promise<void>;
}

interface PanelPosition {
  x: number;
  y: number;
}

const STORAGE_KEY = 'metadata-panel-position';
const DEFAULT_POSITION: PanelPosition = { x: 50, y: 50 };

export function DraggableMetadataPanel({ 
  item, 
  isOpen, 
  onClose, 
  onSave 
}: DraggableMetadataPanelProps) {
  const [position, setPosition] = useState<PanelPosition>(DEFAULT_POSITION);
  const [activeTab, setActiveTab] = useState<'tags' | 'metadata'>('tags');
  const [isSaving, setIsSaving] = useState(false);

  // Load saved position from localStorage
  useEffect(() => {
    const savedPosition = localStorage.getItem(STORAGE_KEY);
    if (savedPosition) {
      try {
        const parsed = JSON.parse(savedPosition);
        setPosition(parsed);
      } catch {
        // Invalid saved position, use default
      }
    }
  }, []);

  // Save position to localStorage when it changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(position));
  }, [position]);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: 'metadata-panel',
    data: {
      type: 'panel',
    },
  });

  const style = {
    transform: transform ? CSS.Translate.toString(transform) : undefined,
    left: position.x,
    top: position.y,
    zIndex: 50,
  };

  const handleSave = async (metadata: any) => {
    if (!item) return;
    
    setIsSaving(true);
    try {
      await onSave(metadata);
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen || !item) {
    return null;
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`fixed w-96 shadow-lg border bg-background rounded-lg ${
        isDragging ? 'shadow-2xl' : ''
      }`}
      {...attributes}
    >
      <Card className="border-0 shadow-none">
        {/* Draggable Header */}
        <CardHeader className="pb-3">
          <div 
            className="flex items-center gap-2 cursor-move"
            {...listeners}
          >
            <GripHorizontal className="h-4 w-4 text-muted-foreground" />
            <div className="flex items-center gap-2 flex-1">
              {item.type === 'file' ? (
                <Settings className="h-4 w-4" />
              ) : (
                <Settings className="h-4 w-4" />
              )}
              <span className="font-medium text-sm">Edit Metadata</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-6 w-6 p-0"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="truncate">{item.name}</span>
            <Badge variant="outline" className="text-xs">
              {item.type}
            </Badge>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-1 mt-2">
            <Button
              variant={activeTab === 'tags' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('tags')}
              className="h-7 px-3 text-xs"
            >
              <Tag className="mr-1 h-3 w-3" />
              Tags
            </Button>
            <Button
              variant={activeTab === 'metadata' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('metadata')}
              className="h-7 px-3 text-xs"
            >
              <Palette className="mr-1 h-3 w-3" />
              Properties
            </Button>
          </div>
        </CardHeader>

        <CardContent className="pt-0">
          <ScrollArea className="h-[400px] pr-4">
            {activeTab === 'tags' && (
              <QuickTagEditor
                item={item}
                onSave={handleSave}
                isSaving={isSaving}
              />
            )}
            
            {activeTab === 'metadata' && (
              <MetadataForm
                item={item}
                onSave={handleSave}
                isSaving={isSaving}
              />
            )}
          </ScrollArea>

          <Separator className="my-4" />

          {/* System Info */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>System Information</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs text-muted-foreground">
              <div>
                <span className="font-medium">Created:</span>
                <br />
                {new Date().toLocaleDateString()}
              </div>
              <div>
                <span className="font-medium">Modified:</span>
                <br />
                {new Date().toLocaleDateString()}
              </div>
              {item.type === 'file' && (
                <div>
                  <span className="font-medium">Word Count:</span>
                  <br />
                  0 words
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}