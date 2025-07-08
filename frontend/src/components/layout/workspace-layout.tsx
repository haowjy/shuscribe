"use client";

import { useState, useRef } from "react";
import { ImperativePanelHandle } from "react-resizable-panels";
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
import { getProjectDisplayData } from "@/data/projects";
import { cn } from "@/lib/utils";
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

interface WorkspaceLayoutProps {
  projectId?: string;
  fileExplorer?: React.ReactNode;
  editor?: React.ReactNode;
  aiPanel?: React.ReactNode;
}

export function WorkspaceLayout({
  projectId,
  fileExplorer,
  editor,
  aiPanel,
}: WorkspaceLayoutProps) {
  const [isFileExplorerCollapsed, setIsFileExplorerCollapsed] = useState(false);
  const [isAiPanelCollapsed, setIsAiPanelCollapsed] = useState(false);
  const fileExplorerRef = useRef<ImperativePanelHandle>(null);
  const aiPanelRef = useRef<ImperativePanelHandle>(null);
  const { user, signOut } = useAuth();

  // Get project data - will be replaced with API call
  const currentProject = getProjectDisplayData(projectId || "");

  const toggleFileExplorer = () => {
    if (fileExplorerRef.current) {
      if (isFileExplorerCollapsed) {
        fileExplorerRef.current.expand();
      } else {
        fileExplorerRef.current.collapse();
      }
    }
  };

  const toggleAiPanel = () => {
    if (aiPanelRef.current) {
      if (isAiPanelCollapsed) {
        aiPanelRef.current.expand();
      } else {
        aiPanelRef.current.collapse();
      }
    }
  };

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
                  {currentProject.wordCount.toLocaleString()} words
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
          <div className="text-sm text-muted-foreground">
            Auto-saved
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="gap-2">
                <User className="h-4 w-4" />
                <span className="hidden sm:inline">
                  {user?.email || "User"}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="flex flex-col space-y-1 p-2">
                <p className="text-sm font-medium leading-none">
                  {user?.user_metadata?.full_name || "User"}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email}
                </p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => signOut()}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Main workspace */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup
          direction="horizontal"
          className="h-full"
        >
          {/* File Explorer Panel */}
          <ResizablePanel
            ref={fileExplorerRef}
            defaultSize={20}
            minSize={15}
            maxSize={40}
            collapsible={true}
            collapsedSize={3}
            onCollapse={() => setIsFileExplorerCollapsed(true)}
            onExpand={() => setIsFileExplorerCollapsed(false)}
            className="bg-secondary/30"
          >
            <div className="h-full flex flex-col">
              <div className="h-10 border-b flex items-center justify-between px-2">
                {!isFileExplorerCollapsed ? (
                  <>
                    <span className="text-sm font-medium flex items-center gap-2">
                      <Files className="h-4 w-4" />
                      Explorer
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleFileExplorer}
                      className="p-1 h-auto"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                  </>
                ) : (
                  <div className="w-full flex justify-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleFileExplorer}
                      className="p-1 h-auto"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
              {!isFileExplorerCollapsed && (
                <div className="flex-1 p-2">
                  {fileExplorer || (
                    <div className="text-sm text-muted-foreground">
                      No project loaded
                    </div>
                  )}
                </div>
              )}
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* Editor Panel */}
          <ResizablePanel defaultSize={55} minSize={30}>
            <div className="h-full bg-background">
              {editor || (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  Select a document to edit
                </div>
              )}
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* AI Panel */}
          <ResizablePanel
            ref={aiPanelRef}
            defaultSize={25}
            minSize={20}
            maxSize={40}
            collapsible={true}
            collapsedSize={3}
            onCollapse={() => setIsAiPanelCollapsed(true)}
            onExpand={() => setIsAiPanelCollapsed(false)}
            className="bg-secondary/30"
          >
            <div className="h-full flex flex-col">
              <div className="h-10 border-b flex items-center justify-between px-2">
                {!isAiPanelCollapsed ? (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleAiPanel}
                      className="p-1 h-auto"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                    <span className="text-sm font-medium flex items-center gap-2">
                      <Bot className="h-4 w-4" />
                      AI Assistant
                    </span>
                  </>
                ) : (
                  <div className="w-full flex justify-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleAiPanel}
                      className="p-1 h-auto"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
              {!isAiPanelCollapsed && (
                <div className="flex-1 p-4">
                  {aiPanel || (
                    <div className="text-sm text-muted-foreground">
                      AI features coming soon
                    </div>
                  )}
                </div>
              )}
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
}