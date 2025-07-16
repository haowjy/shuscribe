"use client";

import { useState, useCallback, useRef, useEffect } from "react";
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
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { RichEditor } from "@/components/editor";
import { EditorDocument } from "@/lib/editor";
import { cn } from "@/lib/utils";
import { Tag } from "@/data/file-tree";

// Import EditorTab type from workspace
import type { EditorTab } from "./workspace-layout";

interface EditorPaneProps {
  tabs: EditorTab[];
  activeTabId: string | null;
  fileTree: any[]; // For @-references
  onTabActivate: (tabId: string) => void;
  onTabClose: (tabId: string) => void;
  onTabReorder: (activeId: string, overId: string) => void;
  onCloseAllTabs: () => void;
  onCloseOthers?: (tabId: string) => void;
  onCloseToRight?: (tabId: string) => void;
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
  onCloseOthers?: (tabId: string) => void;
  onCloseAll?: () => void;
  onCloseToRight?: (tabId: string) => void;
}

function SortableTab({ tab, isActive, onActivate, onClose, onCloseOthers, onCloseAll, onCloseToRight }: SortableTabProps) {
  const [contextMenuOpen, setContextMenuOpen] = useState(false);
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

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenuOpen(true);
  };

  return (
    <>
      <div
        ref={setNodeRef}
        style={style}
        data-tab-id={tab.id}
        onContextMenu={handleContextMenu}
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
            <div className="flex items-center gap-1 min-w-0 flex-1">
              <span className="truncate">{tab.title}</span>
              {/* Tags display - left aligned with title */}
              {tab.tags && tab.tags.length > 0 && (
                <div className="flex items-center gap-1 ml-1">
                  {tab.tags.slice(0, 2).map((tag, index) => (
                    <span
                      key={tag.id}
                      className="inline-block w-2 h-2 rounded-full opacity-60"
                      style={{ backgroundColor: tag.color || '#3b82f6' }}
                      title={tag.name}
                    />
                  ))}
                  {tab.tags.length > 2 && (
                    <span className="text-xs text-muted-foreground">+{tab.tags.length - 2}</span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Close button / Dirty indicator container - shared position */}
          <div className="absolute right-1 top-1/2 -translate-y-1/2 h-4 w-4 flex items-center justify-center">
            {/* Close button - shown on hover */}
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onClose(tab.id);
              }}
              className="relative z-10 h-4 w-4 p-0 opacity-0 group-hover:opacity-100 hover:bg-destructive/20 transition-opacity duration-200 pointer-events-auto"
            >
              <X className="h-3 w-3" />
            </Button>

            {/* Status indicator - dirty, saving, or clean */}
            {tab.isSaving ? (
              <div className="absolute h-2 w-2 bg-blue-500 rounded-full animate-pulse group-hover:opacity-0 transition-opacity duration-200 pointer-events-none" />
            ) : tab.isDirty ? (
              <div className="absolute h-2 w-2 bg-orange-500 rounded-full group-hover:opacity-0 transition-opacity duration-200 pointer-events-none" />
            ) : null}
          </div>
        </div>
      
      {/* Separate Context Menu - only shows on right-click */}
      <DropdownMenu open={contextMenuOpen} onOpenChange={setContextMenuOpen}>
        <DropdownMenuTrigger asChild>
          <div style={{ position: 'fixed', top: -9999, left: -9999, pointerEvents: 'none' }} />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48">
          <DropdownMenuItem
            onClick={() => {
              onClose(tab.id);
              setContextMenuOpen(false);
            }}
          >
            <X className="h-4 w-4 mr-2" />
            Close
          </DropdownMenuItem>
          
          {onCloseOthers && (
            <DropdownMenuItem
              onClick={() => {
                onCloseOthers(tab.id);
                setContextMenuOpen(false);
              }}
            >
              <X className="h-4 w-4 mr-2" />
              Close Others
            </DropdownMenuItem>
          )}
          
          {onCloseToRight && (
            <DropdownMenuItem
              onClick={() => {
                onCloseToRight(tab.id);
                setContextMenuOpen(false);
              }}
            >
              <X className="h-4 w-4 mr-2" />
              Close to Right
            </DropdownMenuItem>
          )}
          
          {onCloseAll && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => {
                  onCloseAll();
                  setContextMenuOpen(false);
                }}
                className="text-destructive focus:text-destructive"
              >
                <X className="h-4 w-4 mr-2" />
                Close All
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  );
}

export function EditorPane({
  tabs,
  activeTabId,
  fileTree,
  onTabActivate,
  onTabClose,
  onTabReorder,
  onCloseAllTabs,
  onCloseOthers,
  onCloseToRight,
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
      onTabReorder(active.id as string, over.id as string);
    }
  }, [onTabReorder]);

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

  // Handle wheel scroll in tab bar with non-passive event listener
  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        const { scrollWidth, clientWidth, scrollLeft } = viewport;
        
        // Only handle horizontal scrolling if tabs overflow
        if (scrollWidth > clientWidth) {
          const scrollAmount = e.deltaY * 0.5;
          const newScrollLeft = scrollLeft + scrollAmount;
          
          // Check if we can actually scroll in the intended direction
          const canScrollLeft = newScrollLeft > 0;
          const canScrollRight = newScrollLeft < scrollWidth - clientWidth;
          
          // Prevent default if we can scroll horizontally
          if ((scrollAmount > 0 && canScrollRight) || (scrollAmount < 0 && canScrollLeft)) {
            e.preventDefault();
            e.stopPropagation();
            viewport.scrollBy({ left: scrollAmount, behavior: 'auto' });
          }
        }
      }
    }
  }, []);

  // Add non-passive wheel event listener to handle horizontal scrolling properly
  useEffect(() => {
    const scrollArea = scrollAreaRef.current;
    if (!scrollArea) return;

    const viewport = scrollArea.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
    if (!viewport) return;

    const handleWheelNative = (e: WheelEvent) => {
      const { scrollWidth, clientWidth, scrollLeft } = viewport;
      
      // Only handle if tabs overflow
      if (scrollWidth > clientWidth) {
        const scrollAmount = e.deltaY * 0.5;
        const newScrollLeft = scrollLeft + scrollAmount;
        
        // Check if we can scroll in the intended direction
        const canScrollLeft = newScrollLeft > 0;
        const canScrollRight = newScrollLeft < scrollWidth - clientWidth;
        
        if ((scrollAmount > 0 && canScrollRight) || (scrollAmount < 0 && canScrollLeft)) {
          e.preventDefault();
          e.stopPropagation();
          viewport.scrollBy({ left: scrollAmount, behavior: 'auto' });
        }
      }
    };

    // Add non-passive event listener
    viewport.addEventListener('wheel', handleWheelNative, { passive: false });

    return () => {
      viewport.removeEventListener('wheel', handleWheelNative);
    };
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
                      onCloseOthers={onCloseOthers}
                      onCloseAll={onCloseAllTabs}
                      onCloseToRight={onCloseToRight}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>

        {/* All Tabs Dropdown - Always visible when there are tabs */}
        {tabs.length > 0 && (
          <DropdownMenu 
            open={isDropdownOpen} 
            onOpenChange={setIsDropdownOpen}
          >
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-full rounded-none border-l px-2 flex-shrink-0 min-w-[2rem]"
                title="All tabs"
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
                  className={cn(
                    "flex items-center gap-2 group",
                    activeTabId === tab.id && "bg-accent"
                  )}
                >
                  {/* Main clickable area */}
                  <div 
                    className="flex items-center gap-2 flex-1 min-w-0"
                    onClick={() => {
                      onTabActivate(tab.id);
                      setIsDropdownOpen(false);
                    }}
                  >
                    {tab.isTemp && <FileEdit className="h-3 w-3 text-muted-foreground" />}
                    <span className="flex-1 truncate">{tab.title}</span>
                  </div>
                  
                  {/* Close button / Dirty indicator */}
                  <div className="relative h-4 w-4 flex items-center justify-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onTabClose(tab.id);
                      }}
                      className="relative z-10 h-4 w-4 p-0 opacity-0 group-hover:opacity-100 hover:bg-destructive/20 transition-opacity duration-200 pointer-events-auto"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                    
                    {/* Status indicator - dirty, saving, or clean */}
                    {tab.isSaving ? (
                      <div className="absolute h-2 w-2 bg-blue-500 rounded-full animate-pulse group-hover:opacity-0 transition-opacity duration-200 pointer-events-none" />
                    ) : tab.isDirty ? (
                      <div className="absolute h-2 w-2 bg-orange-500 rounded-full group-hover:opacity-0 transition-opacity duration-200 pointer-events-none" />
                    ) : null}
                  </div>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => {
                  onCloseAllTabs();
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
          className="h-full rounded-none border-l px-3 flex-shrink-0 min-w-[2.5rem]"
          title="New document"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-hidden h-0">
        {activeTab ? (
          <RichEditor
            key={activeTab.id}
            documentId={activeTab.id}
            initialContent={activeTab.content}
            onChange={handleContentChange}
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
          {activeTab?.isSaving ? (
            <span className="text-blue-600 font-medium">Saving...</span>
          ) : activeTab?.isDirty ? (
            "Modified"
          ) : activeTab?.lastSaved ? (
            `Saved ${activeTab.lastSaved}`
          ) : (
            "Saved"
          )}
        </span>
      </div>
    </div>
  );
}