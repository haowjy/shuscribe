"use client";

import { useState } from "react";
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
import { cn } from "@/lib/utils";
import {
  ChevronLeft,
  ChevronRight,
  Files,
  Bot,
  User,
  LogOut,
  Settings,
} from "lucide-react";

interface WorkspaceLayoutProps {
  fileExplorer?: React.ReactNode;
  editor?: React.ReactNode;
  aiPanel?: React.ReactNode;
}

export function WorkspaceLayout({
  fileExplorer,
  editor,
  aiPanel,
}: WorkspaceLayoutProps) {
  const [isFileExplorerCollapsed, setIsFileExplorerCollapsed] = useState(false);
  const [isAiPanelCollapsed, setIsAiPanelCollapsed] = useState(false);
  const { user, signOut } = useAuth();

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="h-14 border-b flex items-center justify-between px-4 bg-background">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">ShuScribe</h1>
          <div className="text-sm text-muted-foreground">
            Select a project to start
          </div>
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
            defaultSize={20}
            minSize={isFileExplorerCollapsed ? 3 : 15}
            maxSize={40}
            collapsible={true}
            collapsedSize={3}
            onCollapse={() => setIsFileExplorerCollapsed(true)}
            onExpand={() => setIsFileExplorerCollapsed(false)}
            className={cn(
              "bg-secondary/30",
              isFileExplorerCollapsed && "min-w-[48px]"
            )}
          >
            <div className="h-full flex flex-col">
              <div className="h-10 border-b flex items-center justify-between px-2">
                {!isFileExplorerCollapsed ? (
                  <>
                    <span className="text-sm font-medium flex items-center gap-2">
                      <Files className="h-4 w-4" />
                      Explorer
                    </span>
                    <button
                      onClick={() => setIsFileExplorerCollapsed(true)}
                      className="p-1 hover:bg-accent rounded"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setIsFileExplorerCollapsed(false)}
                    className="p-1 hover:bg-accent rounded mx-auto"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
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
            defaultSize={25}
            minSize={isAiPanelCollapsed ? 3 : 20}
            maxSize={40}
            collapsible={true}
            collapsedSize={3}
            onCollapse={() => setIsAiPanelCollapsed(true)}
            onExpand={() => setIsAiPanelCollapsed(false)}
            className={cn(
              "bg-secondary/30",
              isAiPanelCollapsed && "min-w-[48px]"
            )}
          >
            <div className="h-full flex flex-col">
              <div className="h-10 border-b flex items-center justify-between px-2">
                {!isAiPanelCollapsed ? (
                  <>
                    <span className="text-sm font-medium flex items-center gap-2">
                      <Bot className="h-4 w-4" />
                      AI Assistant
                    </span>
                    <button
                      onClick={() => setIsAiPanelCollapsed(true)}
                      className="p-1 hover:bg-accent rounded"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setIsAiPanelCollapsed(false)}
                    className="p-1 hover:bg-accent rounded mx-auto"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
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