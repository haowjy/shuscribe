'use client'

import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable'
import { ChevronsRight } from 'lucide-react'

import { EditorPanel } from '@/components/editor/EditorPanel'
import { RightSidebar } from '@/components/workspace/sidebar/RightSidebar'
import { ContextualDrawer } from '@/components/workspace/contextual/ContextualDrawer'
import { BottomPanel } from '@/components/workspace/bottom-panel/BottomPanel'
import { PanelToggleButton } from './components/PanelToggleButton'

import { PANEL_SIZES, PANEL_IDS } from './constants'
import type { WorkspaceLayoutProps } from './types'

export function WorkspaceLayout({ 
  activityConfig, 
  panelStates, 
  railMode,
  projectId 
}: WorkspaceLayoutProps) {
  // Extract panel states for cleaner access
  const { leftPanel, rightPanel, bottomPanel } = panelStates

  // WorkspaceLayout now only handles the main workspace
  return (
    <div className="h-full bg-background flex overflow-hidden min-w-0">
      <ResizablePanelGroup direction="horizontal" className="h-full min-w-0">
        {/* Left Sidebar - Only render if enabled by activity */}
        {activityConfig.leftPanel.enabled && (
          <>
            <ResizablePanel
              ref={leftPanel.panelRef}
              id={PANEL_IDS.LEFT_SIDEBAR}
              order={1}
              defaultSize={PANEL_SIZES.LEFT_SIDEBAR.default}
              minSize={PANEL_SIZES.LEFT_SIDEBAR.min}
              maxSize={PANEL_SIZES.LEFT_SIDEBAR.max}
              collapsible={true}
              collapsedSize={0}
              onCollapse={leftPanel.onCollapse}
              onExpand={leftPanel.onExpand}
              className="min-w-0"
            >
              <div className="relative h-full min-w-0">
                <ContextualDrawer mode={railMode} onClose={leftPanel.toggle} />
              </div>
            </ResizablePanel>

            {/* Left Edge Handle - Sidebar Toggle */}
            {leftPanel.isCollapsed ? (
              <PanelToggleButton
                icon={ChevronsRight}
                position="left"
                isCollapsed={leftPanel.isCollapsed}
                onToggle={leftPanel.toggle}
                label="Open Sidebar"
                shortcut="⌘B"
              />
            ) : (
              <ResizableHandle />
            )}
          </>
        )}

            {/* Middle Section - Editor and Bottom Panel */}
            <ResizablePanel 
              id={PANEL_IDS.MIDDLE_SECTION}
              order={2}
              defaultSize={PANEL_SIZES.MIDDLE_SECTION.default} 
              minSize={PANEL_SIZES.MIDDLE_SECTION.min}
              className="min-w-0"
            >
              <div className="relative h-full min-w-0">
                <ResizablePanelGroup direction="vertical" className="h-full min-w-0">
                  {/* Editor Panel */}
                  <ResizablePanel 
                    id={PANEL_IDS.EDITOR}
                    order={1}
                    defaultSize={PANEL_SIZES.EDITOR.default} 
                    minSize={PANEL_SIZES.EDITOR.min}
                    className="min-w-0"
                  >
                    <EditorPanel 
                      projectId={projectId}
                      railMode={railMode}
                      leftSidebar={activityConfig.leftPanel.enabled ? {
                        isOpen: !leftPanel.isCollapsed,
                        onToggle: leftPanel.toggle
                      } : undefined}
                      rightSidebar={activityConfig.rightPanel.enabled ? {
                        isOpen: !rightPanel.isCollapsed,
                        onToggle: rightPanel.toggle
                      } : undefined}
                    />
                  </ResizablePanel>

                  {/* Bottom Panel - Only render if enabled by activity */}
                  {activityConfig.bottomPanel.enabled && (
                    <>
                      <ResizableHandle />
                      
                      <ResizablePanel
                        ref={bottomPanel.panelRef}
                        id={PANEL_IDS.BOTTOM_PANEL}
                        order={2}
                        defaultSize={PANEL_SIZES.BOTTOM_PANEL.default}
                        minSize={PANEL_SIZES.BOTTOM_PANEL.min}
                        maxSize={PANEL_SIZES.BOTTOM_PANEL.max}
                        collapsible={true}
                        collapsedSize={6}
                        onCollapse={bottomPanel.onCollapse}
                        onExpand={bottomPanel.onExpand}
                        className="min-w-0"
                      >
                        <BottomPanel 
                          isCollapsed={bottomPanel.isCollapsed}
                          onToggle={bottomPanel.toggle}
                        />
                      </ResizablePanel>
                    </>
                  )}
                </ResizablePanelGroup>
              </div>
            </ResizablePanel>

        {/* Right Sidebar - Only render if enabled by activity */}
        {activityConfig.rightPanel.enabled && (
          <>
            <ResizableHandle />
            
            <ResizablePanel
              ref={rightPanel.panelRef}
              id={PANEL_IDS.RIGHT_SIDEBAR}
              order={3}
              defaultSize={PANEL_SIZES.RIGHT_SIDEBAR.default}
              minSize={PANEL_SIZES.RIGHT_SIDEBAR.min}
              maxSize={PANEL_SIZES.RIGHT_SIDEBAR.max}
              collapsible={true}
              collapsedSize={0}
              onCollapse={rightPanel.onCollapse}
              onExpand={rightPanel.onExpand}
              className="min-w-0"
            >
              <div className="relative h-full min-w-0">
                <RightSidebar onHide={rightPanel.collapse} />
              </div>
            </ResizablePanel>
          </>
        )}

      </ResizablePanelGroup>
    </div>
  )
}

// Re-export types for convenience
export type { WorkspaceLayoutProps, RailMode } from './types'