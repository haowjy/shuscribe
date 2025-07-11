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
// Removed unused import: useProjectDataWithStorage
import { findFileById } from "@/lib/api/file-tree-service";
import { loadDocument } from "@/lib/api/document-service";
import { useActiveFile, useFileTree } from "@/lib/query/hooks";
import { 
  EditorDocument, 
  DraftManager,
  EditorStateManager 
} from "@/lib/editor";
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

export function EditorWorkspace({ projectId }: EditorWorkspaceProps) {
  // Centralized state management
  const { data: fileTree = [], isLoading: isLoadingFileTree, error: fileTreeError } = useFileTree(projectId);
  const { activeTabId, setActiveTab, addTab, removeTab } = useActiveFile(projectId);
  
  // Local state management
  const [tabs, setTabs] = useState<EditorTab[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const preventNextCloseRef = useRef(false);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const tabContainerRef = useRef<HTMLDivElement>(null);

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
    if (!isInitialized && !isLoadingFileTree && fileTree.length > 0) {
      const restoreEditorState = async () => {
        const savedState = EditorStateManager.getState();
        
        if (savedState) {
          if (savedState.openDocuments.length > 0) {
            // Restore saved tabs by loading documents through the new service
            const restoredTabs: EditorTab[] = [];
            
            for (const [index, docId] of savedState.openDocuments.entries()) {
              try {
                const result = await loadDocument(docId);
                const tab: EditorTab = {
                  id: docId,
                  title: result.document.title,
                  content: result.document.content,
                  isDirty: false,
                  isTemp: result.document.isTemp || false,
                  order: savedState.documentOrder[docId] || index,
                };
                restoredTabs.push(tab);
              } catch (error) {
                console.warn(`Failed to restore document ${docId}:`, error);
                // Skip this document but continue with others
              }
            }
            
            if (restoredTabs.length > 0) {
              const sortedTabs = restoredTabs.sort((a, b) => a.order - b.order);
              setTabs(sortedTabs);
              setActiveTabId(savedState.activeDocumentId || sortedTabs[0]?.id || "");
            }
          } else {
            // Respect saved empty state - user closed all tabs intentionally
            setTabs([]);
            setActiveTabId("");
          }
        } else {
          // No saved state - create initial tab from first file in tree (first time user)
          const allFiles = fileTree.flatMap(item => 
            item.type === 'file' ? [item] : 
            item.children?.filter(child => child.type === 'file') || []
          );
          
          if (allFiles.length > 0) {
            const firstFile = allFiles[0];
            try {
              const result = await loadDocument(firstFile.id);
              const initialTab: EditorTab = {
                id: firstFile.id,
                title: result.document.title,
                content: result.document.content,
                isDirty: false,
                isTemp: result.document.isTemp || false,
                order: 0,
              };
              setTabs([initialTab]);
              setActiveTabId(firstFile.id);
            } catch (error) {
              console.warn(`Failed to load initial document ${firstFile.id}:`, error);
            }
          }
        }
        
        setIsInitialized(true);
      };
      
      restoreEditorState();
    }
  }, [fileTree, isLoadingFileTree, isInitialized]);

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
    setActiveTab(tabId);
    
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
  }, [setActiveTab]);

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
  const closeTab = useCallback((tabId: string) => {
    // Use centralized tab removal (this handles active tab switching automatically)
    removeTab(tabId);
    
    // Update local tabs state
    setTabs(prev => prev.filter(tab => tab.id !== tabId));

    // Clean up draft
    DraftManager.removeDraft(tabId);
  }, [removeTab]);

  // Close all tabs
  const closeAllTabs = useCallback(() => {
    // Clean up all drafts
    tabs.forEach(tab => {
      DraftManager.removeDraft(tab.id);
    });
    
    // Clear centralized state
    tabs.forEach(tab => removeTab(tab.id));
    
    // Clear local tabs state
    setTabs([]);
  }, [tabs, removeTab]);

  // Central navigation handler - can be called from any pane
  const handleOpenFile = useCallback(async (fileId: string, source: 'file-explorer' | 'reference' | 'api' = 'file-explorer') => {
    console.log(`🔍 Opening file ${fileId} from ${source}`);
    
    // Validation: Check file ID format
    if (!fileId || typeof fileId !== 'string' || fileId.trim() === '') {
      console.error(`❌ Invalid file ID: "${fileId}"`);
      return;
    }
    
    // Check if tab already exists
    const existingTab = tabs.find(tab => tab.id === fileId);
    if (existingTab) {
      // Tab exists, just activate it
      console.log(`✅ File ${fileId} already open, activating tab`);
      activateTab(fileId);
      return;
    }
    
    // Find file in file tree with detailed logging
    const fileItem = findFileById(fileTree, fileId);
    if (!fileItem) {
      console.error(`❌ File not found in file tree: ${fileId}`);
      console.log(`📋 Available files in tree:`, fileTree.flatMap(item => 
        item.type === 'file' ? [{ id: item.id, name: item.name }] : 
        item.children?.filter(child => child.type === 'file').map(child => ({ id: child.id, name: child.name })) || []
      ));
      
      // For @ references, show user-friendly error
      if (source === 'reference') {
        console.warn(`🔗 Reference points to non-existent file: ${fileId}`);
        // TODO: Show user notification toast
      }
      return;
    }
    
    // Runtime validation: Ensure file IDs match between file tree and reference system
    console.log(`✅ File found in tree: ${fileItem.name} (ID: ${fileItem.id}, Type: ${fileItem.type})`);
    
    // Only handle file types, not folders
    if (fileItem.type === 'folder') {
      console.log(`📁 Folder clicked: ${fileItem.name} (future: filter file explorer)`);
      // TODO: Implement folder filtering in file explorer
      return;
    }
    
    try {
      // Load document using new service
      console.log(`📄 Loading document ${fileId} using document service`);
      const result = await loadDocument(fileId);
      
      if (result.error) {
        console.warn(`⚠️ Document load warning for ${fileId}:`, result.error);
        // Continue with fallback document if available
      }
      
      // Validation: Ensure document ID matches file ID
      if (result.document.id !== fileId) {
        console.warn(`⚠️ Document ID mismatch: file=${fileId}, document=${result.document.id}`);
      }
      
      // Create new tab with loaded document
      const activeTabIndex = tabs.findIndex(tab => tab.id === activeTabId);
      const newOrder = activeTabIndex >= 0 ? tabs[activeTabIndex].order + 0.5 : Math.max(...tabs.map(t => t.order), -1) + 1;
      
      const newTab: EditorTab = {
        id: fileId,
        title: result.document.title,
        content: result.document.content,
        isDirty: false,
        isTemp: result.document.isTemp || false,
        order: newOrder,
      };
      
      console.log(`✅ Creating new tab for file ${fileId}: "${newTab.title}"`);
      
      // Add to centralized state (this also activates the tab)
      addTab(fileId);
      
      // Update local tabs state
      setTabs(prev => {
        const newTabs = [...prev, newTab];
        // Reorder all tabs based on their order values
        return newTabs.sort((a, b) => a.order - b.order).map((tab, index) => ({
          ...tab,
          order: index,
        }));
      });
      
    } catch (error) {
      console.error(`❌ Error opening file ${fileId}:`, error);
      
      // Show user-friendly error for @ references
      if (source === 'reference') {
        console.error(`🔗 Failed to open reference: ${fileId}`);
        // TODO: Show user notification toast
      }
    }
  }, [fileTree, tabs, activeTabId, addTab, activateTab]);


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
  
  // Handle reference click - delegates to central navigation
  const handleReferenceClick = useCallback((referenceId: string, referenceLabel: string) => {
    console.log(`Reference clicked: ${referenceId} (${referenceLabel})`);
    handleOpenFile(referenceId, 'reference');
  }, [handleOpenFile]);

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


  if (isLoadingFileTree) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground">Loading project...</p>
        </div>
      </div>
    );
  }

  if (fileTreeError || fileTree.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-destructive mb-2">Failed to load project</p>
          <p className="text-xs text-muted-foreground">{fileTreeError}</p>
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
            onReferenceClick={handleReferenceClick}
            fileTree={fileTree}
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