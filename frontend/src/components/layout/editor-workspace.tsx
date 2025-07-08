"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { X, Plus, FileEdit, MoreHorizontal, GripVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
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
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import {
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { EditorTab, mockTabs } from "@/data/editor-tabs";
import { FileItem } from "@/data/file-tree";
import { usePersistedEditorState } from "@/hooks/use-persisted-editor-state";
import { FictionEditor } from "@/components/editor/fiction-editor";
import { createEmptyDoc } from "@/lib/prosemirror/schema";
import { cn } from "@/lib/utils";

interface EditorWorkspaceProps {
  selectedFile?: FileItem | null;
  projectId: string;
}

export function EditorWorkspace({ selectedFile, projectId }: EditorWorkspaceProps) {
  const [tabs, setTabs] = useState<EditorTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string>("");
  const [tempFileCounter, setTempFileCounter] = useState(1);
  const [isInitialized, setIsInitialized] = useState(false);
  const initializationRef = useRef(false);
  const lastSelectedFileRef = useRef<FileItem | null>(null);
  const [visibleTabs, setVisibleTabs] = useState<EditorTab[]>([]);
  const [overflowTabs, setOverflowTabs] = useState<EditorTab[]>([]);
  const tabContainerRef = useRef<HTMLDivElement>(null);
  const [maxVisibleTabs, setMaxVisibleTabs] = useState(8); // Default estimate
  const [sortedTabs, setSortedTabs] = useState<EditorTab[]>([]);
  
  // Configure drag sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px of movement before drag starts
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Initialize persistence hooks
  const {
    saveEditorState,
    saveDraft,
    removeDraft,
    hasDraft,
    restoreContentFromDraft,
    loadEditorState,
    ensureTabOrder,
  } = usePersistedEditorState({
    projectId,
  });

  const activeTab = sortedTabs.find(tab => tab.id === activeTabId);
  
  // Sortable Tab Component
  interface SortableTabProps {
    tab: EditorTab;
    isActive: boolean;
    onActivate: (tabId: string) => void;
    onClose: (tabId: string) => void;
    canClose: boolean;
    hasDraft: (tabId: string) => boolean;
  }
  
  function SortableTab({ tab, isActive, onActivate, onClose, canClose, hasDraft }: SortableTabProps) {
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
          "flex items-center px-3 py-2 text-sm border-r cursor-pointer group relative min-w-0 flex-shrink-0",
          isActive 
            ? "bg-background text-foreground border-b-2 border-b-primary" 
            : "hover:bg-secondary/50 text-muted-foreground",
          isDragging && "opacity-50 z-50"
        )}
        onClick={() => onActivate(tab.id)}
      >
        {/* Drag Handle */}
        <div
          {...attributes}
          {...listeners}
          className="opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing mr-1 flex-shrink-0"
        >
          <GripVertical className="h-3 w-3 text-muted-foreground" />
        </div>
        
        <div className="flex items-center gap-1.5 min-w-0 flex-1 relative">
          {tab.isTemp && <FileEdit className="h-3 w-3 flex-shrink-0" />}
          <span className="truncate pr-6">{tab.name}</span>
          {(tab.isDirty || hasDraft(tab.id)) && <span className="text-xs text-orange-500 absolute right-5">•</span>}
          
          {canClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onClose(tab.id);
              }}
              className="absolute right-0 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 h-5 w-5 p-0 transition-opacity bg-background/80 hover:bg-background border border-transparent hover:border-border rounded-sm z-10"
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
    );
  }

  // Create a new untitled file
  const createNewFile = useCallback(() => {
    setTabs(currentTabs => {
      // Generate a unique ID that doesn't conflict with existing tabs
      let newCounter = tempFileCounter;
      let newId = `temp-${newCounter}`;
      
      // Ensure ID is unique
      while (currentTabs.some(tab => tab.id === newId)) {
        newCounter++;
        newId = `temp-${newCounter}`;
      }
      
      // Create empty ProseMirror document
      const emptyDoc = createEmptyDoc();
      
      const newTab: EditorTab = {
        id: newId,
        name: `Untitled-${newCounter}`,
        content: emptyDoc.toJSON(),
        isDirty: true,
        isTemp: true,
        order: Math.max(...currentTabs.map(t => t.order), -1) + 1
      };
      
      // Update counter and set active tab
      setTempFileCounter(newCounter + 1);
      setActiveTabId(newTab.id);
      
      // Save initial draft
      saveDraft(newTab.id, JSON.stringify(newTab.content), true);
      
      return [...currentTabs, newTab];
    });
  }, [tempFileCounter, saveDraft]);

  // Handle file selection - create or switch to tab
  const handleFileSelect = useCallback((file: FileItem) => {
    if (file.type === "folder") return;
    
    setTabs(currentTabs => {
      // Check if tab already exists
      const existingTab = currentTabs.find(tab => tab.id === file.id);
      if (existingTab) {
        // Just switch to existing tab, don't modify tabs array
        setTimeout(() => setActiveTabId(file.id), 0);
        return currentTabs;
      }
      
      // Double-check to prevent race conditions
      const stillExists = currentTabs.find(tab => tab.id === file.id);
      if (stillExists) {
        setTimeout(() => setActiveTabId(file.id), 0);
        return currentTabs;
      }
      
      // Check if we have mock data for this file
      const mockTab = mockTabs.find(tab => 
        tab.name === file.name || 
        tab.filePath === file.name ||
        file.name.includes(tab.name.replace('.md', ''))
      );
      
      // Use mock content if available, otherwise create empty document
      const content = mockTab ? mockTab.content : createEmptyDoc().toJSON();
      
      // Create new tab
      let newTab: EditorTab = {
        id: file.id,
        name: file.name,
        filePath: file.name, // Store the file path separately
        content,
        isDirty: false,
        order: Math.max(...currentTabs.map(t => t.order), -1) + 1
      };
      
      // Restore from draft if available
      newTab = restoreContentFromDraft(newTab);
      
      setTimeout(() => setActiveTabId(file.id), 0);
      
      return [...currentTabs, newTab];
    });
  }, [restoreContentFromDraft]);

  // Effect to handle selectedFile prop
  useEffect(() => {
    if (selectedFile && selectedFile !== lastSelectedFileRef.current) {
      lastSelectedFileRef.current = selectedFile;
      handleFileSelect(selectedFile);
    }
  }, [selectedFile, handleFileSelect]);

  const closeTab = useCallback((tabId: string) => {
    setTabs(currentTabs => {
      // Don't close if it's the last tab
      if (currentTabs.length <= 1) return currentTabs;
      
      const tabIndex = currentTabs.findIndex(tab => tab.id === tabId);
      const newTabs = currentTabs.filter(tab => tab.id !== tabId);
      
      // If closing the active tab, switch to an adjacent tab
      if (tabId === activeTabId) {
        // Try to select the tab to the right, or to the left if it's the last tab
        const newIndex = Math.min(tabIndex, newTabs.length - 1);
        setActiveTabId(newTabs[newIndex].id);
      }
      
      // Clean up draft if exists
      removeDraft(tabId);
      
      return newTabs;
    });
  }, [activeTabId, removeDraft]);

  // Initialize state from localStorage on mount
  useEffect(() => {
    if (!initializationRef.current) {
      initializationRef.current = true;
      const savedState = loadEditorState();
      
      if (savedState && savedState.tabs.length > 0) {
        setTabs(ensureTabOrder(savedState.tabs));
        setActiveTabId(savedState.activeTabId);
        setTempFileCounter(savedState.tempFileCounter);
      } else {
        // Load mock tabs with proper ordering and IDs
        const initialTabs = mockTabs.map((tab, index) => ({
          ...tab,
          order: index,
          id: `mock-${index + 1}` // Give them unique IDs
        }));
        
        setTabs(initialTabs);
        setActiveTabId(initialTabs[0]?.id || '');
        setTempFileCounter(mockTabs.length + 1);
      }
      
      setIsInitialized(true);
    }
  }, [loadEditorState, saveDraft, ensureTabOrder]);
  
  // Save state to localStorage when tabs or activeTabId change (after initialization)
  useEffect(() => {
    if (isInitialized && tabs.length > 0) {
      saveEditorState({
        tabs,
        activeTabId,
        tempFileCounter,
      });
    }
  }, [tabs, activeTabId, tempFileCounter, saveEditorState, isInitialized]);
  
  // Sort tabs by order whenever tabs change
  useEffect(() => {
    const sorted = [...tabs].sort((a, b) => a.order - b.order);
    setSortedTabs(sorted);
  }, [tabs]);
  
  // Handle drag end event
  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    
    if (over && active.id !== over.id) {
      setTabs(currentTabs => {
        const sorted = [...currentTabs].sort((a, b) => a.order - b.order);
        const oldIndex = sorted.findIndex(tab => tab.id === active.id);
        const newIndex = sorted.findIndex(tab => tab.id === over.id);
        
        // Reorder tabs
        const reorderedTabs = arrayMove(sorted, oldIndex, newIndex);
        
        // Update order property based on new positions
        const updatedTabs = reorderedTabs.map((tab, index) => ({
          ...tab,
          order: index
        }));
        
        return updatedTabs;
      });
    }
  }, []);
  
  // Calculate visible and overflow tabs
  const calculateTabVisibility = useCallback(() => {
    if (sortedTabs.length === 0) {
      setVisibleTabs([]);
      setOverflowTabs([]);
      return;
    }
    
    // Always prioritize showing the active tab
    const activeTabIndex = sortedTabs.findIndex(tab => tab.id === activeTabId);
    
    if (sortedTabs.length <= maxVisibleTabs) {
      // All tabs fit, show them all
      setVisibleTabs(sortedTabs);
      setOverflowTabs([]);
    } else {
      // Need to split tabs
      let visibleStartIndex = 0;
      let visibleEndIndex = maxVisibleTabs;
      
      // If active tab is beyond visible range, adjust window
      if (activeTabIndex >= maxVisibleTabs) {
        visibleStartIndex = Math.max(0, activeTabIndex - Math.floor(maxVisibleTabs / 2));
        visibleEndIndex = Math.min(sortedTabs.length, visibleStartIndex + maxVisibleTabs);
        
        // Adjust start if we're near the end
        if (visibleEndIndex === sortedTabs.length) {
          visibleStartIndex = Math.max(0, sortedTabs.length - maxVisibleTabs);
        }
      }
      
      const visible = sortedTabs.slice(visibleStartIndex, visibleEndIndex);
      const overflow = [
        ...sortedTabs.slice(0, visibleStartIndex),
        ...sortedTabs.slice(visibleEndIndex)
      ];
      
      setVisibleTabs(visible);
      setOverflowTabs(overflow);
    }
  }, [sortedTabs, activeTabId, maxVisibleTabs]);
  
  // Bring an overflow tab to visible area (replace last visible tab)
  const bringTabToVisible = useCallback((tabId: string) => {
    if (sortedTabs.length <= maxVisibleTabs) {
      // All tabs are already visible, just recalculate normally
      calculateTabVisibility();
      return;
    }
    
    // Find the tab to bring forward
    const tabIndex = sortedTabs.findIndex(tab => tab.id === tabId);
    if (tabIndex === -1) return;
    
    // Current visible window calculation (same logic as calculateTabVisibility)
    const activeTabIndex = sortedTabs.findIndex(tab => tab.id === activeTabId);
    let visibleStartIndex = 0;
    let visibleEndIndex = maxVisibleTabs;
    
    // Adjust window if active tab is beyond visible range
    if (activeTabIndex >= maxVisibleTabs) {
      visibleStartIndex = Math.max(0, activeTabIndex - Math.floor(maxVisibleTabs / 2));
      visibleEndIndex = Math.min(sortedTabs.length, visibleStartIndex + maxVisibleTabs);
      
      if (visibleEndIndex === sortedTabs.length) {
        visibleStartIndex = Math.max(0, sortedTabs.length - maxVisibleTabs);
      }
    }
    
    // Check if tab is already visible
    if (tabIndex >= visibleStartIndex && tabIndex < visibleEndIndex) {
      // Tab is already visible, just activate it
      setActiveTabId(tabId);
      return;
    }
    
    // Tab is in overflow, need to bring it to visible area
    // Strategy: Replace the last visible tab with the selected tab
    const currentVisible = sortedTabs.slice(visibleStartIndex, visibleEndIndex);
    const currentOverflow = [
      ...sortedTabs.slice(0, visibleStartIndex),
      ...sortedTabs.slice(visibleEndIndex)
    ];
    
    // Remove the selected tab from overflow
    const selectedTab = sortedTabs[tabIndex];
    const newOverflow = currentOverflow.filter(tab => tab.id !== tabId);
    
    // Replace last visible tab with selected tab
    const lastVisibleTab = currentVisible[currentVisible.length - 1];
    const newVisible = [
      ...currentVisible.slice(0, -1), // All visible except last
      selectedTab // Replace last with selected
    ];
    
    // Add the displaced tab to overflow
    const updatedOverflow = [...newOverflow, lastVisibleTab];
    
    setVisibleTabs(newVisible);
    setOverflowTabs(updatedOverflow);
    setActiveTabId(tabId);
  }, [sortedTabs, maxVisibleTabs, activeTabId, calculateTabVisibility]);
  
  // Update tab visibility when sorted tabs or active tab changes
  useEffect(() => {
    calculateTabVisibility();
  }, [calculateTabVisibility]);
  
  // Recalculate max visible tabs based on container width
  useEffect(() => {
    const updateMaxVisibleTabs = () => {
      if (tabContainerRef.current) {
        const containerWidth = tabContainerRef.current.parentElement?.clientWidth || 800;
        // Estimate tab width (120px content + 24px padding + 16px close button + 1px border)
        const estimatedTabWidth = 161;
        // Reserve space for overflow dropdown (40px) and new tab button (40px)
        const availableWidth = containerWidth - 80;
        const maxTabs = Math.max(1, Math.floor(availableWidth / estimatedTabWidth));
        setMaxVisibleTabs(maxTabs);
      }
    };
    
    updateMaxVisibleTabs();
    
    // Add resize listener
    const resizeObserver = new ResizeObserver(updateMaxVisibleTabs);
    if (tabContainerRef.current?.parentElement) {
      resizeObserver.observe(tabContainerRef.current.parentElement);
    }
    
    return () => resizeObserver.disconnect();
  }, []);

  // Handle content changes and save drafts
  const handleContentChange = useCallback((tabId: string, content: object) => {
    // Update tab content
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, content, isDirty: true }
        : tab
    ));
    
    // Save draft (convert to string for localStorage)
    saveDraft(tabId, JSON.stringify(content), true);
  }, [saveDraft]);

  return (
    <div className="h-full flex flex-col">
      {/* Tab Bar */}
      <div className="flex items-center border-b bg-secondary/20">
        {/* Scrollable Tabs */}
        <div className="flex-1 min-w-0">
          <ScrollArea className="w-full">
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={visibleTabs.map(tab => tab.id)}
                strategy={horizontalListSortingStrategy}
              >
                <div 
                  ref={tabContainerRef}
                  className="flex items-center"
                >
                  {visibleTabs.map((tab) => (
                    <SortableTab
                      key={tab.id}
                      tab={tab}
                      isActive={activeTabId === tab.id}
                      onActivate={setActiveTabId}
                      onClose={closeTab}
                      canClose={tabs.length > 1}
                      hasDraft={hasDraft}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>
        
        {/* Overflow Dropdown */}
        {overflowTabs.length > 0 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                className="px-2 text-muted-foreground flex-shrink-0 border-l"
              >
                <MoreHorizontal className="h-4 w-4" />
                <span className="ml-1 text-xs">{overflowTabs.length}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {overflowTabs.map((tab) => (
                <DropdownMenuItem
                  key={tab.id}
                  onClick={() => {
                    // Bring the overflow tab to visible area
                    bringTabToVisible(tab.id);
                  }}
                  className={cn(
                    "flex items-center justify-between",
                    activeTabId === tab.id && "bg-accent"
                  )}
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    {tab.isTemp && <FileEdit className="h-3 w-3 flex-shrink-0" />}
                    <span className="truncate">{tab.name}</span>
                    {(tab.isDirty || hasDraft(tab.id)) && <span className="text-xs text-orange-500">•</span>}
                  </div>
                  {tabs.length > 1 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        closeTab(tab.id);
                      }}
                      className="h-auto p-0.5 ml-2 opacity-70 hover:opacity-100"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
        
        {/* New Tab Button */}
        <Button 
          variant="ghost" 
          size="sm" 
          className="px-2 text-muted-foreground flex-shrink-0 border-l"
          onClick={createNewFile}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Editor Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab ? (
          <FictionEditor
            key={activeTab.id}
            content={activeTab.content}
            onChange={(content: object) => handleContentChange(activeTab.id, content)}
            onUpdate={(content: object) => handleContentChange(activeTab.id, content)}
            placeholder={activeTab.isTemp ? "Start writing your story here..." : `Edit ${activeTab.name}`}
            className="h-full"
          />
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            No document open
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="h-6 bg-secondary/20 border-t flex items-center justify-between px-4 text-xs text-muted-foreground">
        <span>
          {activeTab ? 'Fiction document' : 'No document'}
        </span>
        <span>
          {(activeTab?.isDirty || (activeTab && hasDraft(activeTab.id))) ? "Modified" : "Saved"}
          {activeTab?.isTemp && " • Unsaved file"}
        </span>
      </div>
    </div>
  );
}