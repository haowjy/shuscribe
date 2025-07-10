"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { X, Plus, FileEdit, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import { RichEditor } from "@/components/editor";
import { 
  useDocumentWithStorage, 
  useCreateDocumentWithStorage,
  useSaveDocument,
  useProjectDataWithStorage 
} from "@/lib/query/enhanced-hooks";
import { 
  EditorDocument, 
  DocumentState,
  DraftManager,
  EditorStateManager 
} from "@/lib/editor";
import { FileItem } from "@/data/file-tree";
import { cn } from "@/lib/utils";

// Simplified tab interface
export interface EditorTab {
  id: string;
  title: string;
  content: EditorDocument;
  isDirty: boolean;
  isTemp: boolean;
  order: number;
}

interface EditorWorkspaceProps {
  selectedFile?: FileItem | null;
  projectId: string;
}

// Sortable Tab Component
interface SortableTabProps {
  tab: EditorTab;
  isActive: boolean;
  onActivate: (tabId: string) => void;
  onClose: (tabId: string) => void;
  hasDraft: boolean;
}

function SortableTab({ tab, isActive, onActivate, onClose, hasDraft }: SortableTabProps) {
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
      className={cn(
        "group relative flex items-center px-4 py-2 text-sm border-r cursor-pointer min-w-[120px] max-w-[200px] flex-shrink-0",
        isActive
          ? "bg-background text-foreground border-b-2 border-b-primary"
          : "hover:bg-secondary/50 text-muted-foreground bg-secondary/20",
        isDragging && "opacity-50 z-50"
      )}
      onClick={() => onActivate(tab.id)}
      {...attributes}
      {...listeners}
    >
      <div className="flex items-center gap-2 min-w-0 flex-1">
        {tab.isTemp && <FileEdit className="h-3 w-3 flex-shrink-0 text-muted-foreground" />}
        <span className="truncate">{tab.title}</span>
        {(tab.isDirty || hasDraft) && (
          <span className="text-xs text-orange-500 flex-shrink-0">•</span>
        )}
      </div>

      <Button
        variant="ghost"
        size="sm"
        onClick={(e) => {
          e.stopPropagation();
          onClose(tab.id);
        }}
        className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 h-5 w-5 p-0 transition-opacity hover:bg-destructive/10"
      >
        <X className="h-3 w-3" />
      </Button>
    </div>
  );
}

export function EditorWorkspace({ selectedFile, projectId }: EditorWorkspaceProps) {
  // State management
  const [tabs, setTabs] = useState<EditorTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string>("");
  const [isInitialized, setIsInitialized] = useState(false);
  const [tempCounter, setTempCounter] = useState(1);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const tabContainerRef = useRef<HTMLDivElement>(null);
  
  // Data fetching
  const { data: projectData, isLoading: projectLoading, error: projectError } = useProjectDataWithStorage(projectId);
  const createDocumentMutation = useCreateDocumentWithStorage();
  const saveDocumentMutation = useSaveDocument();

  // Active tab data
  const activeTab = tabs.find(tab => tab.id === activeTabId);
  const { data: activeDocumentData } = useDocumentWithStorage(activeTabId);

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

  // Load saved editor state on mount
  useEffect(() => {
    if (!isInitialized && projectData) {
      const savedState = EditorStateManager.getState();
      
      if (savedState) {
        if (savedState.openDocuments.length > 0) {
          // Restore saved tabs
          const restoredTabs: EditorTab[] = savedState.openDocuments.map((docId, index) => {
            const projectDoc = projectData.documents.find(d => d.id === docId);
            return {
              id: docId,
              title: projectDoc?.title || `Document ${docId}`,
              content: projectDoc?.content || { type: 'doc', content: [{ type: 'paragraph' }] },
              isDirty: false,
              isTemp: false,
              order: savedState.documentOrder[docId] || index,
            };
          }).sort((a, b) => a.order - b.order);
          
          setTabs(restoredTabs);
          setActiveTabId(savedState.activeDocumentId || restoredTabs[0]?.id || "");
        } else {
          // Respect saved empty state - user closed all tabs intentionally
          setTabs([]);
          setActiveTabId("");
        }
      } else {
        // No saved state - create initial tab from first document (first time user)
        const firstDoc = projectData.documents[0];
        if (firstDoc) {
          const initialTab: EditorTab = {
            id: firstDoc.id,
            title: firstDoc.title,
            content: firstDoc.content,
            isDirty: false,
            isTemp: false,
            order: 0,
          };
          setTabs([initialTab]);
          setActiveTabId(firstDoc.id);
        }
      }
      
      setIsInitialized(true);
    }
  }, [projectData, isInitialized]);

  // Save editor state when tabs change (including empty state)
  useEffect(() => {
    if (isInitialized) {
      const state = {
        activeDocumentId: activeTabId,
        openDocuments: tabs.map(t => t.id),
        documentOrder: Object.fromEntries(tabs.map(t => [t.id, t.order])),
        lastModified: Date.now(),
      };
      EditorStateManager.saveState(state);
    }
  }, [tabs, activeTabId, isInitialized]);

  // Handle file selection
  const handleFileSelect = useCallback((file: FileItem) => {
    if (file.type === "folder" || !projectData) return;

    // Check if tab already exists
    const existingTab = tabs.find(tab => tab.id === file.id);
    if (existingTab) {
      setActiveTabId(file.id);
      return;
    }

    // Find document data
    const document = projectData.documents.find(doc => doc.id === file.id);
    if (!document) return;

    // Create new tab
    const newTab: EditorTab = {
      id: file.id,
      title: document.title,
      content: document.content,
      isDirty: false,
      isTemp: false,
      order: Math.max(...tabs.map(t => t.order), -1) + 1,
    };

    setTabs(prev => [...prev, newTab]);
    setActiveTabId(file.id);
  }, [tabs, projectData]);

  // Handle selectedFile prop
  useEffect(() => {
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  }, [selectedFile, handleFileSelect]);

  // Create new temporary document
  const createNewDocument = useCallback(async () => {
    const newTab: EditorTab = {
      id: `temp-${Date.now()}-${tempCounter}`,
      title: `Untitled-${tempCounter}`,
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      isDirty: true,
      isTemp: true,
      order: Math.max(...tabs.map(t => t.order), -1) + 1,
    };

    setTabs(prev => [...prev, newTab]);
    setActiveTabId(newTab.id);
    setTempCounter(prev => prev + 1);
  }, [tabs, tempCounter]);

  // Close tab
  const closeTab = useCallback((tabId: string) => {
    setTabs(prev => {
      const newTabs = prev.filter(tab => tab.id !== tabId);
      
      // If closing active tab, switch to adjacent tab
      if (tabId === activeTabId) {
        const tabIndex = prev.findIndex(tab => tab.id === tabId);
        if (newTabs.length === 0) {
          setActiveTabId("");
        } else {
          const newIndex = Math.min(tabIndex, newTabs.length - 1);
          setActiveTabId(newTabs[newIndex].id);
        }
      }
      
      return newTabs;
    });

    // Clean up draft
    DraftManager.removeDraft(tabId);
  }, [activeTabId]);

  // Handle drag end
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setTabs(tabs => {
        const oldIndex = tabs.findIndex(tab => tab.id === active.id);
        const newIndex = tabs.findIndex(tab => tab.id === over.id);
        
        const reorderedTabs = arrayMove(tabs, oldIndex, newIndex);
        
        return reorderedTabs.map((tab, index) => ({
          ...tab,
          order: index,
        }));
      });
    }
  }, []);

  // Handle content changes
  const handleContentChange = useCallback(async (content: EditorDocument) => {
    if (!activeTabId) return;

    // Update tab content and mark as dirty
    setTabs(prev => prev.map(tab => 
      tab.id === activeTabId 
        ? { ...tab, content, isDirty: true }
        : tab
    ));

    // Auto-save will be handled by the editor component
  }, [activeTabId]);

  // Check scroll state
  const checkScrollState = useCallback(() => {
    if (scrollAreaRef.current) {
      // Access the actual scrollable viewport element inside the ScrollArea
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        const { scrollLeft, scrollWidth, clientWidth } = viewport;
        setCanScrollLeft(scrollLeft > 0);
        setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
      }
    }
  }, []);

  // Handle scroll events
  const handleScroll = useCallback(() => {
    checkScrollState();
  }, [checkScrollState]);

  // Scroll controls with better sensitivity
  const scrollLeft = useCallback(() => {
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        const scrollAmount = Math.min(150, viewport.clientWidth / 3);
        viewport.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
      }
    }
  }, []);

  const scrollRight = useCallback(() => {
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        const scrollAmount = Math.min(150, viewport.clientWidth / 3);
        viewport.scrollBy({ left: scrollAmount, behavior: 'smooth' });
      }
    }
  }, []);

  // Handle wheel scroll
  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (scrollAreaRef.current) {
      // Access the actual scrollable viewport element inside the ScrollArea
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        // Check if there's actually scrollable content
        const { scrollWidth, clientWidth } = viewport;
        if (scrollWidth > clientWidth) {
          e.preventDefault();
          const scrollAmount = e.deltaY * 0.5; // Adjust sensitivity
          viewport.scrollBy({ left: scrollAmount, behavior: 'auto' });
        }
      }
    }
  }, []);

  // Check scroll state when tabs change
  useEffect(() => {
    checkScrollState();
  }, [tabs, checkScrollState]);

  // Monitor scroll state with ResizeObserver
  useEffect(() => {
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      if (viewport) {
        // Check initial state
        checkScrollState();
        
        // Create ResizeObserver to detect container size changes
        const resizeObserver = new ResizeObserver(() => {
          checkScrollState();
        });
        
        resizeObserver.observe(viewport);
        
        return () => {
          resizeObserver.disconnect();
        };
      }
    }
  }, [checkScrollState]);

  if (projectLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground">Loading project...</p>
        </div>
      </div>
    );
  }

  if (projectError || !projectData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-destructive mb-2">Failed to load project</p>
          <p className="text-xs text-muted-foreground">{projectError?.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Tab Bar */}
      <div className="flex items-center border-b bg-secondary/10 h-10">
        {/* Scroll Left Button */}
        {canScrollLeft && (
          <Button
            variant="ghost"
            size="sm"
            onClick={scrollLeft}
            className="h-full rounded-none border-r px-2"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        )}

        {/* Tabs */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea 
            ref={scrollAreaRef} 
            className="w-full"
            onScroll={handleScroll}
          >
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={tabs.map(tab => tab.id)}
                strategy={horizontalListSortingStrategy}
              >
                <div 
                  ref={tabContainerRef} 
                  className="flex"
                  onWheel={handleWheel}
                >
                  {tabs.map(tab => (
                    <SortableTab
                      key={tab.id}
                      tab={tab}
                      isActive={activeTabId === tab.id}
                      onActivate={setActiveTabId}
                      onClose={closeTab}
                      hasDraft={DraftManager.hasDraft(tab.id)}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>

        {/* Scroll Right Button */}
        {canScrollRight && (
          <Button
            variant="ghost"
            size="sm"
            onClick={scrollRight}
            className="h-full rounded-none border-l px-2"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        )}

        {/* New Tab Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={createNewDocument}
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
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-lg text-muted-foreground mb-2">No documents open</p>
              <p className="text-sm text-muted-foreground mb-4">
                Select a file from the explorer or create a new document
              </p>
              <Button onClick={createNewDocument} variant="outline">
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
          {activeTab?.isDirty || (activeTab && DraftManager.hasDraft(activeTab.id)) ? "Modified" : "Saved"}
        </span>
      </div>
    </div>
  );
}