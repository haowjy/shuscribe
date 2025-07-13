"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { ImperativePanelHandle } from "react-resizable-panels";
import { usePersistedLayout } from "@/hooks/use-persisted-layout";
import { loadDocument } from "@/lib/api/document-service";
import { useProjectData, useFileTree, useUpdateDocument } from "@/lib/query/hooks";
import { EditorDocument } from "@/lib/editor";
import { findItemById } from "@/lib/api/file-tree-service";
import { isFile } from "@/data/file-tree";
import { FileExplorer } from "./file-explorer";
import { EditorPane } from "./editor-pane";
import { AiPanel } from "./ai-panel";

// Panel size constants
const PANEL_CONFIG = {
  fileExplorer: {
    minSize: 10,
    maxSize: 35,
    collapsedSize: 2,
    collapseThreshold: 4,
  },
  aiPanel: {
    minSize: 20,
    maxSize: 40,
    collapsedSize: 2,
    collapseThreshold: 4,
  },
} as const;

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/contexts/auth-context";
import {
  ChevronLeft,
  ChevronRight,
  Files,
  Bot,
  User,
  LogOut,
  Settings,
  FolderOpen,
  ChevronDown,
  Plus,
} from "lucide-react";

// Simple Tab Interface
export interface EditorTab {
  id: string;
  title: string;
  content: EditorDocument;
  isDirty: boolean;
  isTemp: boolean;
  isSaving?: boolean;
  lastSaved?: string;
}

interface WorkspaceLayoutProps {
  projectId: string;
}

export function WorkspaceLayout({ projectId }: WorkspaceLayoutProps) {
  // Panel layout state
  const [isFileExplorerCollapsed, setIsFileExplorerCollapsed] = useState(false);
  const [isAiPanelCollapsed, setIsAiPanelCollapsed] = useState(false);
  const [fileExplorerSize, setFileExplorerSize] = useState(20);
  const [editorSize, setEditorSize] = useState(55);
  const [aiPanelSize, setAiPanelSize] = useState(25);
  
  // MASTER EDITOR STATE - Single Source of Truth
  const [openTabs, setOpenTabs] = useState<EditorTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);
  
  const fileExplorerRef = useRef<ImperativePanelHandle>(null);
  const aiPanelRef = useRef<ImperativePanelHandle>(null);
  const { user, signOut } = useAuth();
  
  // Data hooks
  const { data: projectData, isLoading: isLoadingProject, error: projectError } = useProjectData(projectId);
  const { data: fileTree = [], isLoading: isLoadingFileTree } = useFileTree(projectId);
  const updateDocumentMutation = useUpdateDocument();
  
  // Initialize layout persistence
  const {
    updatePanelSizes,
    updateCollapsedStates,
  } = usePersistedLayout({
    projectId,
    onLayoutLoaded: (layout) => {
      setFileExplorerSize(layout.fileExplorerSize);
      setEditorSize(layout.editorSize);
      setAiPanelSize(layout.aiPanelSize);
      setIsFileExplorerCollapsed(layout.isFileExplorerCollapsed);
      setIsAiPanelCollapsed(layout.isAiPanelCollapsed);
    },
  });

  // Handle project data loading states
  const currentProject = {
    title: projectData?.title || "Loading...",
    wordCount: projectData?.word_count || 0
  };
  
  if (projectError) {
    currentProject.title = "Error loading project";
  }

  // MASTER CONTROLLER FUNCTIONS

  // Open file - The main controller function
  const handleFileOpen = useCallback(async (treeItemId: string) => {
    console.log('🎯 [WorkspaceLayout] Opening file with TreeItem ID:', treeItemId);
    
    // Find file in tree
    const treeItem = findItemById(fileTree, treeItemId);
    if (!treeItem || !isFile(treeItem)) {
      console.error('🎯 [WorkspaceLayout] File not found in tree:', treeItemId);
      return;
    }
    
    // Extract document ID from the file tree item
    const documentId = treeItem.document_id;
    if (!documentId) {
      console.error('🎯 [WorkspaceLayout] File has no document_id:', treeItem);
      return;
    }
    
    console.log('🎯 [WorkspaceLayout] Document ID extracted:', documentId);
    
    // Check if document is already open (using document ID)
    const existingTab = openTabs.find(tab => tab.id === documentId);
    if (existingTab) {
      console.log('🎯 [WorkspaceLayout] Document already open, activating tab');
      setActiveTabId(documentId);
      return;
    }
    
    try {
      // Load document using document ID
      console.log('🎯 [WorkspaceLayout] Loading document from API with document ID');
      const result = await loadDocument(documentId);
      
      // Create new tab using document ID
      const newTab: EditorTab = {
        id: documentId, // Use document ID as tab ID
        title: result.document.title,
        content: result.document.content,
        isDirty: false,
        isTemp: result.document.isTemp || false,
      };
      
      console.log('🎯 [WorkspaceLayout] Creating new tab:', newTab.title, 'with document ID:', documentId);
      
      // Update state
      setOpenTabs(prev => [...prev, newTab]);
      setActiveTabId(documentId);
      
    } catch (error) {
      console.error('🎯 [WorkspaceLayout] Failed to open document:', error);
    }
  }, [fileTree, openTabs]);

  // Close tab
  const handleTabClose = useCallback((tabId: string) => {
    console.log('🎯 [WorkspaceLayout] Closing tab:', tabId);
    
    setOpenTabs(prev => prev.filter(tab => tab.id !== tabId));
    
    // Switch active tab if needed
    if (activeTabId === tabId) {
      const remainingTabs = openTabs.filter(tab => tab.id !== tabId);
      setActiveTabId(remainingTabs.length > 0 ? remainingTabs[remainingTabs.length - 1].id : null);
    }
  }, [activeTabId, openTabs]);

  // Save document with optimistic updates
  const handleDocumentSave = useCallback(async (tabId: string) => {
    const tab = openTabs.find(t => t.id === tabId);
    if (!tab) return false;
    
    console.log('💾 [WorkspaceLayout] Starting optimistic save for tab:', tabId);
    
    // Immediate optimistic update - show saving state immediately
    setOpenTabs(prev => prev.map(t => 
      t.id === tabId 
        ? { ...t, isSaving: true, isDirty: false }
        : t
    ));
    
    try {
      // Background API save
      await updateDocumentMutation.mutateAsync({
        documentId: tabId,
        updates: {
          content: tab.content,
          title: tab.title
        }
      });
      
      // Success - update final state
      setOpenTabs(prev => prev.map(t => 
        t.id === tabId 
          ? { ...t, isSaving: false, isDirty: false, lastSaved: new Date().toLocaleTimeString() }
          : t
      ));
      
      console.log('💾 [WorkspaceLayout] Save completed successfully for tab:', tabId);
      return true;
    } catch (error) {
      console.error('💾 [WorkspaceLayout] Save failed for tab:', tabId, error);
      
      // Error - revert optimistic state
      setOpenTabs(prev => prev.map(t => 
        t.id === tabId 
          ? { ...t, isSaving: false, isDirty: true } // Revert to dirty state
          : t
      ));
      
      return false;
    }
  }, [openTabs, updateDocumentMutation]);

  // Content change
  const handleContentChange = useCallback((tabId: string, content: EditorDocument) => {
    setOpenTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, content, isDirty: true }
        : tab
    ));
  }, []);

  // Tab reordering
  const handleTabReorder = useCallback((activeId: string, overId: string) => {
    console.log('🎯 [WorkspaceLayout] Reordering tabs:', activeId, 'to position of', overId);
    
    setOpenTabs(prev => {
      const oldIndex = prev.findIndex(tab => tab.id === activeId);
      const newIndex = prev.findIndex(tab => tab.id === overId);
      
      if (oldIndex === -1 || newIndex === -1) {
        console.warn('🎯 [WorkspaceLayout] Invalid tab indices for reordering:', { oldIndex, newIndex });
        return prev;
      }
      
      // Use arrayMove-like logic
      const result = [...prev];
      const [reorderedItem] = result.splice(oldIndex, 1);
      result.splice(newIndex, 0, reorderedItem);
      
      console.log('🎯 [WorkspaceLayout] Tabs reordered successfully');
      return result;
    });
  }, []);

  // Close all tabs
  const handleCloseAllTabs = useCallback(() => {
    console.log('🎯 [WorkspaceLayout] Closing all tabs');
    setOpenTabs([]);
    setActiveTabId(null);
  }, []);

  // Create new document
  const handleCreateNewDocument = useCallback(() => {
    const timestamp = Date.now();
    const newTab: EditorTab = {
      id: `temp-${timestamp}`,
      title: `Untitled`,
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      isDirty: true,
      isTemp: true,
    };
    
    console.log('🎯 [WorkspaceLayout] Creating new document:', newTab.title);
    
    setOpenTabs(prev => [...prev, newTab]);
    setActiveTabId(newTab.id);
  }, []);

  // Panel control functions (keeping existing logic)
  const toggleFileExplorer = () => {
    if (fileExplorerRef.current) {
      const newState = !isFileExplorerCollapsed;
      if (newState) {
        fileExplorerRef.current.collapse();
      } else {
        fileExplorerRef.current.expand();
      }
      updateCollapsedStates({ isFileExplorerCollapsed: newState });
    }
  };

  const toggleAiPanel = () => {
    if (aiPanelRef.current) {
      const newState = !isAiPanelCollapsed;
      if (newState) {
        aiPanelRef.current.collapse();
      } else {
        aiPanelRef.current.expand();
      }
      updateCollapsedStates({ isAiPanelCollapsed: newState });
    }
  };
  
  // Handle panel resize events (keeping existing logic)
  const handlePanelResize = (sizes: number[]) => {
    const [newFileExplorerSize, newEditorSize, newAiPanelSize] = sizes;
    setFileExplorerSize(newFileExplorerSize);
    setEditorSize(newEditorSize);
    setAiPanelSize(newAiPanelSize);
    
    const fileExplorerShouldBeCollapsed = isFileExplorerCollapsed 
      ? newFileExplorerSize < PANEL_CONFIG.fileExplorer.collapseThreshold
      : newFileExplorerSize <= PANEL_CONFIG.fileExplorer.collapseThreshold;
    const aiPanelShouldBeCollapsed = isAiPanelCollapsed
      ? newAiPanelSize < PANEL_CONFIG.aiPanel.collapseThreshold
      : newAiPanelSize <= PANEL_CONFIG.aiPanel.collapseThreshold;
    
    if (fileExplorerShouldBeCollapsed !== isFileExplorerCollapsed) {
      setIsFileExplorerCollapsed(fileExplorerShouldBeCollapsed);
    }
    
    if (aiPanelShouldBeCollapsed !== isAiPanelCollapsed) {
      setIsAiPanelCollapsed(aiPanelShouldBeCollapsed);
    }
    
    updatePanelSizes({
      fileExplorerSize: newFileExplorerSize,
      editorSize: newEditorSize,
      aiPanelSize: newAiPanelSize,
    });
    
    updateCollapsedStates({
      isFileExplorerCollapsed: fileExplorerShouldBeCollapsed,
      isAiPanelCollapsed: aiPanelShouldBeCollapsed,
    });
  };
  
  // Apply collapsed states when layout is loaded
  useEffect(() => {
    if (isFileExplorerCollapsed && fileExplorerRef.current) {
      fileExplorerRef.current.collapse();
    }
    if (isAiPanelCollapsed && aiPanelRef.current) {
      aiPanelRef.current.collapse();
    }
  }, [isFileExplorerCollapsed, isAiPanelCollapsed]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="h-14 border-b flex items-center justify-between px-4 bg-background">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">ShuScribe</h1>
          <div className="h-6 w-px bg-border" />
          
          {/* Project Selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="gap-2 max-w-64">
                <FolderOpen className="h-4 w-4" />
                <span className="truncate">{currentProject.title}</span>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-64">
              <div className="p-2">
                <div className="text-xs font-medium text-muted-foreground mb-2">
                  Current Project
                </div>
                <div className="text-sm font-medium">{currentProject.title}</div>
                <div className="text-xs text-muted-foreground">
                  {isLoadingProject ? "Loading..." : `${currentProject.wordCount.toLocaleString()} words`}
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => window.location.href = '/dashboard'}>
                <FolderOpen className="mr-2 h-4 w-4" />
                Switch Project
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => window.location.href = '/dashboard/new'}>
                <Plus className="mr-2 h-4 w-4" />
                New Project
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="flex items-center gap-4">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="gap-2">
                <User className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {user?.email || "User"}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => signOut()}>
                <LogOut className="mr-2 h-4 w-4" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup
          direction="horizontal"
          onLayout={handlePanelResize}
          className="h-full"
        >
          {/* File Explorer Panel */}
          <ResizablePanel
            ref={fileExplorerRef}
            defaultSize={fileExplorerSize}
            minSize={PANEL_CONFIG.fileExplorer.minSize}
            maxSize={PANEL_CONFIG.fileExplorer.maxSize}
            collapsedSize={PANEL_CONFIG.fileExplorer.collapsedSize}
            collapsible={true}
            onCollapse={() => setIsFileExplorerCollapsed(true)}
            onExpand={() => setIsFileExplorerCollapsed(false)}
          >
            <div className="h-full border-r bg-background flex flex-col">
              <div className="flex items-center justify-between p-2 border-b flex-shrink-0">
                <div className="flex items-center gap-2">
                  <Files className="h-4 w-4" />
                  {!isFileExplorerCollapsed && <span className="text-sm font-medium">Files</span>}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleFileExplorer}
                  className="h-6 w-6 p-0"
                >
                  {isFileExplorerCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
                </Button>
              </div>
              {!isFileExplorerCollapsed && (
                <div className="flex-1 overflow-hidden">
                  <FileExplorer 
                    projectId={projectId}
                    onFileClick={handleFileOpen}
                  />
                </div>
              )}
            </div>
          </ResizablePanel>

          <ResizableHandle />

          {/* Editor Panel */}
          <ResizablePanel defaultSize={editorSize} minSize={30}>
            <EditorPane
              tabs={openTabs}
              activeTabId={activeTabId}
              fileTree={fileTree}
              onTabActivate={setActiveTabId}
              onTabClose={handleTabClose}
              onTabReorder={handleTabReorder}
              onCloseAllTabs={handleCloseAllTabs}
              onContentChange={handleContentChange}
              onSave={handleDocumentSave}
              onCreateNew={handleCreateNewDocument}
            />
          </ResizablePanel>

          <ResizableHandle />

          {/* AI Panel */}
          <ResizablePanel
            ref={aiPanelRef}
            defaultSize={aiPanelSize}
            minSize={PANEL_CONFIG.aiPanel.minSize}
            maxSize={PANEL_CONFIG.aiPanel.maxSize}
            collapsedSize={PANEL_CONFIG.aiPanel.collapsedSize}
            collapsible={true}
            onCollapse={() => setIsAiPanelCollapsed(true)}
            onExpand={() => setIsAiPanelCollapsed(false)}
          >
            <div className="h-full border-l bg-background flex flex-col">
              <div className="flex items-center justify-between p-2 border-b flex-shrink-0">
                <div className="flex items-center gap-2">
                  {!isAiPanelCollapsed && <span className="text-sm font-medium">AI Assistant</span>}
                  <Bot className="h-4 w-4" />
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleAiPanel}
                  className="h-6 w-6 p-0"
                >
                  {isAiPanelCollapsed ? <ChevronLeft className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                </Button>
              </div>
              {!isAiPanelCollapsed && (
                <div className="flex-1 overflow-hidden">
                  <AiPanel />
                </div>
              )}
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
}