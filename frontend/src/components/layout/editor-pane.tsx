"use client";

import { useState, useCallback, useRef } from "react";
import { Plus, X, FileEdit, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import { restrictToHorizontalAxis } from "@dnd-kit/modifiers";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { RichEditor } from "@/components/editor";
import { EditorDocument } from "@/lib/editor";
import { cn } from "@/lib/utils";

// Import EditorTab type from workspace
import type { EditorTab } from "./workspace-layout";

interface EditorPaneProps {
  tabs: EditorTab[];
  activeTabId: string | null;
  fileTree: any[]; // For @-references
  onTabActivate: (tabId: string) => void;
  onTabClose: (tabId: string) => void;
  onContentChange: (tabId: string, content: EditorDocument) => void;
  onSave: (tabId: string) => Promise<boolean>;
  onCreateNew: () => void;
}

// Sortable Tab Component
interface SortableTabProps {
  tab: EditorTab;
  isActive: boolean;
  onActivate: (tabId: string) => void;
  onClose: (tabId: string) => void;
}

function SortableTab({ tab, isActive, onActivate, onClose }: SortableTabProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: tab.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      data-tab-id={tab.id}
      className={cn(
        "group relative flex items-center text-sm border-r cursor-pointer min-w-[120px] max-w-[200px] flex-shrink-0",
        isActive
          ? "bg-background text-foreground border-b-2 border-b-primary"
          : "hover:bg-secondary/50 text-muted-foreground bg-secondary/20",
        isDragging && "opacity-50 z-[9999]"
      )}
    >
      {/* Drag handle area */}
      <div 
        className="flex items-center gap-2 min-w-0 flex-1 pr-6 py-2 pl-2"
        onClick={() => onActivate(tab.id)}
        {...attributes}
        {...listeners}
      >
        {tab.isTemp && <FileEdit className="h-2 w-2 flex-shrink-0 text-muted-foreground" />}
        <span className="truncate">{tab.title}</span>
      </div>

      {/* Close button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={(e) => {
          e.stopPropagation();
          onClose(tab.id);
        }}
        className="absolute right-1 top-1/2 -translate-y-1/2 h-4 w-4 p-0 opacity-0 group-hover:opacity-100 hover:bg-destructive/20"
      >
        <X className="h-3 w-3" />
      </Button>

      {/* Dirty indicator */}
      {tab.isDirty && (
        <div className="absolute right-1 top-1/2 -translate-y-1/2 h-2 w-2 bg-orange-500 rounded-full" />
      )}
    </div>
  );
}

export function EditorPane({
  tabs,
  activeTabId,
  fileTree,
  onTabActivate,
  onTabClose,
  onContentChange,
  onSave,
  onCreateNew,
}: EditorPaneProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Find active tab
  const activeTab = tabs.find(tab => tab.id === activeTabId);

  // Drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Handle drag end (tab reordering)
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      // Tab reordering logic would go here
      console.log('Tab reorder:', active.id, 'to position of', over.id);
    }
  }, []);

  // Handle content changes
  const handleContentChange = useCallback((content: EditorDocument) => {
    if (activeTabId) {
      onContentChange(activeTabId, content);
    }
  }, [activeTabId, onContentChange]);

  // Handle save
  const handleSave = useCallback(async () => {
    if (activeTabId) {
      return await onSave(activeTabId);
    }
    return false;
  }, [activeTabId, onSave]);

  // Handle wheel scroll in tab bar
  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        const { scrollWidth, clientWidth } = viewport;
        if (scrollWidth > clientWidth) {
          e.preventDefault();
          const scrollAmount = e.deltaY * 0.5;
          viewport.scrollBy({ left: scrollAmount, behavior: 'auto' });
        }
      }
    }
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* Tab Bar */}
      <div className="flex items-center border-b bg-secondary/10 h-10">
        {/* Tabs */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea 
            ref={scrollAreaRef} 
            className="w-full"
          >
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              modifiers={[restrictToHorizontalAxis]}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={tabs.map(tab => tab.id)}
                strategy={horizontalListSortingStrategy}
              >
                <div 
                  className="flex"
                  onWheel={handleWheel}
                >
                  {tabs.map(tab => (
                    <SortableTab
                      key={tab.id}
                      tab={tab}
                      isActive={activeTabId === tab.id}
                      onActivate={onTabActivate}
                      onClose={onTabClose}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>

        {/* All Tabs Dropdown */}
        {tabs.length > 1 && (
          <DropdownMenu 
            open={isDropdownOpen} 
            onOpenChange={setIsDropdownOpen}
          >
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-full rounded-none border-l px-2"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent 
              align="end" 
              className="max-h-80 overflow-y-auto w-64"
            >
              <DropdownMenuLabel>All Tabs</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {tabs.map((tab) => (
                <DropdownMenuItem
                  key={tab.id}
                  onClick={() => {
                    onTabActivate(tab.id);
                    setIsDropdownOpen(false);
                  }}
                  className={cn(
                    "flex items-center gap-2",
                    activeTabId === tab.id && "bg-accent"
                  )}
                >
                  {tab.isTemp && <FileEdit className="h-3 w-3 text-muted-foreground" />}
                  <span className="flex-1 truncate">{tab.title}</span>
                  {tab.isDirty && (
                    <div className="h-2 w-2 bg-orange-500 rounded-full" />
                  )}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => {
                  // Close all tabs logic would go here
                  console.log('Close all tabs');
                  setIsDropdownOpen(false);
                }}
                className="flex items-center gap-2 text-destructive focus:text-destructive"
              >
                <X className="h-3 w-3" />
                <span>Close All Tabs</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {/* New Tab Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onCreateNew}
          className="h-full rounded-none border-l px-3"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab ? (
          <RichEditor
            key={activeTab.id}
            documentId={activeTab.id}
            initialContent={activeTab.content}
            onContentChange={handleContentChange}
            placeholder={activeTab.isTemp ? "Start writing..." : `Edit ${activeTab.title}`}
            enableAutoSave={true}
            enableDrafts={true}
            autofocus={true}
            className="h-full"
            isSaving={activeTab.isSaving}
            lastSaved={activeTab.lastSaved}
            onSave={handleSave}
            onReferenceClick={(refId, refLabel) => {
              console.log('Reference clicked:', refId, refLabel);
              // This would trigger file opening via parent workspace
            }}
            fileTree={fileTree}
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-lg text-muted-foreground mb-2">No documents open</p>
              <p className="text-sm text-muted-foreground mb-4">
                Select a file from the explorer or create a new document
              </p>
              <Button onClick={onCreateNew} variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                New Document
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="h-6 bg-secondary/10 border-t flex items-center justify-between px-4 text-xs text-muted-foreground">
        <span>
          {activeTab ? `${activeTab.title}${activeTab.isTemp ? ' (unsaved)' : ''}` : 'No document'}
        </span>
        <span>
          {activeTab?.isDirty ? "Modified" : "Saved"}
        </span>
      </div>
    </div>
  );
}