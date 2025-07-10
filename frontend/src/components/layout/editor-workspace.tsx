"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Plus, FileEdit, MoreHorizontal, X } from "lucide-react";
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
import { 
  useProjectDataWithStorage 
} from "@/lib/query/enhanced-hooks";
import { 
  EditorDocument, 
  DraftManager,
  EditorStateManager 
} from "@/lib/editor";
import { FileItem } from "@/data/file-tree";
import { TabStatusIndicator } from "./tab-status-indicator";
import { cn } from "@/lib/utils";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { useBeforeUnloadProtection, hasAnyUnsavedChanges } from "@/hooks/use-beforeunload-protection";
import { documentsApi } from "@/lib/api/mock-documents";

// Simplified tab interface
export interface EditorTab {
  id: string;
  title: string;
  content: EditorDocument;
  isDirty: boolean;
  isTemp: boolean;
  order: number;
  isSaving?: boolean;
  lastSaved?: string;
}

interface EditorWorkspaceProps {
  selectedFile?: FileItem | null;
  projectId: string;
  onFileDeselect?: (fileId: string) => void;
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
      data-tab-id={tab.id}
      className={cn(
        "group relative flex items-center text-sm border-r cursor-pointer min-w-[120px] max-w-[200px] flex-shrink-0",
        isActive
          ? "bg-background text-foreground border-b-2 border-b-primary"
          : "hover:bg-secondary/50 text-muted-foreground bg-secondary/20",
        isDragging && "opacity-50 z-[9999]"
      )}
    >
      {/* Drag handle area - takes up most of the tab */}
      <div 
        className="flex items-center gap-2 min-w-0 flex-1 pr-6 py-2 pl-2"
        onClick={() => onActivate(tab.id)}
        {...attributes}
        {...listeners}
      >
        {tab.isTemp && <FileEdit className="h-2 w-2 flex-shrink-0 text-muted-foreground" />}
        <span className="truncate">{tab.title}</span>
      </div>

      <TabStatusIndicator
        isDirty={tab.isDirty}
        hasDraft={hasDraft}
        isSaving={tab.isSaving}
        lastSaved={tab.lastSaved}
        onClose={() => onClose(tab.id)}
        variant="tab"
      />
    </div>
  );
}

export function EditorWorkspace({ selectedFile, projectId, onFileDeselect }: EditorWorkspaceProps) {
  // State management
  const [tabs, setTabs] = useState<EditorTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string>("");
  const [isInitialized, setIsInitialized] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const preventNextCloseRef = useRef(false);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const tabContainerRef = useRef<HTMLDivElement>(null);
  
  // Data fetching
  const { data: projectData, isLoading: projectLoading, error: projectError } = useProjectDataWithStorage(projectId);

  // Active tab data
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

  // Handle tab activation with auto-scroll
  const activateTab = useCallback((tabId: string, skipAutoScroll = false) => {
    setActiveTabId(tabId);
    
    // Skip auto-scroll if requested (e.g., when called from dropdown)
    if (skipAutoScroll) return;
    
    // Use setTimeout to ensure DOM is updated before scrolling
    setTimeout(() => {
      if (!scrollAreaRef.current) return;
      
      const viewport = scrollAreaRef.current.querySelector('[data-slot="scroll-area-viewport"]') as HTMLElement;
      const tabElement = viewport?.querySelector(`[data-tab-id="${tabId}"]`) as HTMLElement;
      
      if (viewport && tabElement) {
        const tabRect = tabElement.getBoundingClientRect();
        const viewportRect = viewport.getBoundingClientRect();
        
        // Check if tab is already fully visible
        const isFullyVisible = tabRect.left >= viewportRect.left && tabRect.right <= viewportRect.right;
        
        if (!isFullyVisible) {
          // Calculate scroll position to center the tab in view
          const tabCenter = tabRect.left + tabRect.width / 2;
          const viewportCenter = viewportRect.left + viewportRect.width / 2;
          const scrollAmount = tabCenter - viewportCenter;
          
          viewport.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
      }
    }, 0);
  }, []);

  // Helper function to find lowest available untitled number
  const getLowestAvailableUntitledNumber = useCallback(() => {
    const untitledNumbers = tabs
      .filter(tab => tab.title.startsWith('Untitled-'))
      .map(tab => {
        const match = tab.title.match(/^Untitled-(\d+)$/);
        return match ? parseInt(match[1], 10) : 0;
      })
      .filter(num => num > 0);

    // Find the lowest available number starting from 1
    for (let i = 1; i <= untitledNumbers.length + 1; i++) {
      if (!untitledNumbers.includes(i)) {
        return i;
      }
    }
    return 1; // Fallback
  }, [tabs]);

  // Create new temporary document
  const createNewDocument = useCallback(async () => {
    const untitledNumber = getLowestAvailableUntitledNumber();
    const newTab: EditorTab = {
      id: `temp-${Date.now()}-${untitledNumber}`,
      title: `Untitled-${untitledNumber}`,
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      isDirty: true,
      isTemp: true,
      order: Math.max(...tabs.map(t => t.order), -1) + 1,
    };

    setTabs(prev => [...prev, newTab]);
    activateTab(newTab.id);
  }, [tabs, getLowestAvailableUntitledNumber, activateTab]);

  // Close tab
  const closeTab = useCallback((tabId: string, fromDropdown = false) => {
    setTabs(prev => {
      const newTabs = prev.filter(tab => tab.id !== tabId);
      
      // If closing active tab, switch to adjacent tab
      if (tabId === activeTabId) {
        const tabIndex = prev.findIndex(tab => tab.id === tabId);
        if (newTabs.length === 0) {
          setActiveTabId("");
        } else {
          const newIndex = Math.min(tabIndex, newTabs.length - 1);
          // Skip auto-scroll when closing from dropdown to prevent dropdown from closing
          activateTab(newTabs[newIndex].id, fromDropdown);
        }
      }
      
      return newTabs;
    });

    // Notify parent that file should be deselected
    onFileDeselect?.(tabId);

    // Clean up draft
    DraftManager.removeDraft(tabId);
  }, [activeTabId, activateTab, onFileDeselect]);

  // Close all tabs
  const closeAllTabs = useCallback(() => {
    // Clean up all drafts
    tabs.forEach(tab => {
      DraftManager.removeDraft(tab.id);
      // Notify parent that each file should be deselected
      onFileDeselect?.(tab.id);
    });
    
    // Clear all tabs and active tab
    setTabs([]);
    setActiveTabId("");
  }, [tabs, onFileDeselect]);

  // Handle file selection
  const handleFileSelect = useCallback((file: FileItem) => {
    if (file.type === "folder" || !projectData) return;

    // Check if tab already exists
    const existingTab = tabs.find(tab => tab.id === file.id);
    if (existingTab) {
      activateTab(file.id);
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
    activateTab(file.id);
  }, [tabs, projectData, activateTab]);

  // Handle selectedFile prop
  useEffect(() => {
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  }, [selectedFile, handleFileSelect]);

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

  // Save current document
  const saveCurrentDocument = useCallback(async () => {
    if (!activeTab) return false;
    
    // Update tab to show saving state
    setTabs(prev => prev.map(tab => 
      tab.id === activeTab.id 
        ? { ...tab, isSaving: true }
        : tab
    ));

    try {
      const response = await documentsApi.saveDocument(activeTab.id, activeTab.content, activeTab.title);
      
      if (response.success) {
        // Update tab with successful save
        setTabs(prev => prev.map(tab => 
          tab.id === activeTab.id 
            ? { 
                ...tab, 
                isDirty: false, 
                isSaving: false,
                lastSaved: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              }
            : tab
        ));
        
        // Clear draft since document is now saved
        DraftManager.removeDraft(activeTab.id);
        return true;
      } else {
        throw new Error(response.error || 'Save failed');
      }
    } catch (error) {
      // Update tab to show save failed
      setTabs(prev => prev.map(tab => 
        tab.id === activeTab.id 
          ? { ...tab, isSaving: false }
          : tab
      ));
      
      console.error('Save failed:', error);
      return false;
    }
  }, [activeTab]);


  // Keyboard shortcuts (only Ctrl+S works reliably across browsers)
  useKeyboardShortcuts({
    onSave: saveCurrentDocument,
  });

  // Protect against accidental data loss when closing tab/browser
  const hasUnsaved = hasAnyUnsavedChanges(tabs);
  useBeforeUnloadProtection(hasUnsaved);

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
                  ref={tabContainerRef} 
                  className="flex"
                  onWheel={handleWheel}
                >
                  {tabs.map(tab => (
                    <SortableTab
                      key={tab.id}
                      tab={tab}
                      isActive={activeTabId === tab.id}
                      onActivate={activateTab}
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

        {/* All Tabs Dropdown */}
        {tabs.length > 1 && (
          <DropdownMenu 
            open={isDropdownOpen} 
            onOpenChange={(open) => {
              // Always allow opening
              if (open) {
                setIsDropdownOpen(true);
                return;
              }
              
              // For closing: check if we should prevent this close
              if (preventNextCloseRef.current) {
                // Reset the flag and prevent closing
                preventNextCloseRef.current = false;
                return;
              }
              
              // Allow normal closing (outside clicks, escape key, etc.)
              setIsDropdownOpen(false);
            }}
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
              className="max-h-80 overflow-y-auto"
              style={{ 
                width: '17rem', /* 272px - slightly wider to account for scrollbar */
                scrollbarGutter: 'stable' /* Reserve space for scrollbar */
              }}
            >
              <DropdownMenuLabel>All Tabs</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {tabs.map((tab) => (
                <DropdownMenuItem
                  key={tab.id}
                  onSelect={(event) => {
                    // Prevent dropdown auto-close - we handle activation manually
                    event.preventDefault();
                  }}
                  className={cn(
                    "flex items-center gap-2 group",
                    activeTabId === tab.id && "bg-accent"
                  )}
                >
                  {tab.isTemp && <FileEdit className="h-3 w-3 text-muted-foreground" />}
                  <span 
                    className="flex-1 truncate cursor-pointer" 
                    onClick={(e) => {
                      e.stopPropagation();
                      activateTab(tab.id);
                      setIsDropdownOpen(false);
                    }}
                  >
                    {tab.title}
                  </span>
                  <TabStatusIndicator
                    isDirty={tab.isDirty}
                    hasDraft={DraftManager.hasDraft(tab.id)}
                    isSaving={tab.isSaving}
                    lastSaved={tab.lastSaved}
                    onClose={(e) => {
                      e?.preventDefault();
                      e?.stopPropagation();
                      // Prevent the next dropdown close event
                      preventNextCloseRef.current = true;
                      closeTab(tab.id, true); // fromDropdown = true
                      // Keep dropdown open for multiple closures
                    }}
                    variant="dropdown"
                  />
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => {
                  closeAllTabs();
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
            isSaving={activeTab.isSaving}
            lastSaved={activeTab.lastSaved}
            onSave={async () => {
              const success = await saveCurrentDocument();
              return success;
            }}
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