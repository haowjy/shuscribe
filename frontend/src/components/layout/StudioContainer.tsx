'use client'

import { useCallback, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { TooltipProvider } from '@/components/ui/tooltip'

import { StudioLeftRail } from './StudioLeftRail'
import { WorkspaceLayout } from '@/components/workspace/layout/WorkspaceLayout'
import { DevToolsPage } from '@/components/debug/DevToolsPage'
import { SettingsPage } from '@/components/app/SettingsPage'
import { ComponentGallery } from '@/components/debug/ComponentGallery'
import { ToastProvider } from '@/components/providers/ToastProvider'
import { SettingsModal } from '@/components/app/SettingsModal'
import { useWorkspaceShortcuts } from '@/components/workspace/layout/hooks/useWorkspaceShortcuts'
import { usePanelState } from '@/components/workspace/layout/hooks/usePanelState'
import { BookOpen, Plus, FileText, Share2, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { ProjectStateProvider, useProjectState } from '@/components/providers/ProjectStateProvider'
import type { RailMode } from '@/components/workspace/layout/types'

// Extend RailMode to include 'studio' for studio list view
export type StudioRailMode = 'studio' | 'workspace' | 'component-gallery' | 'devtools' | 'settings' | 'series' | 'articles'

interface ActivityConfiguration {
  leftPanel: { enabled: boolean; defaultOpen: boolean }
  rightPanel: { enabled: boolean; defaultOpen: boolean }
  bottomPanel: { enabled: boolean; defaultOpen: boolean }
}

// Configuration for different activities
const EXPLORER_CONFIGURATION: ActivityConfiguration = {
  leftPanel: { enabled: true, defaultOpen: true },
  rightPanel: { enabled: true, defaultOpen: true },
  bottomPanel: { enabled: true, defaultOpen: false }
}

// Other activities don't need panels - they take full content area
const TOOL_CONFIGURATION: ActivityConfiguration = {
  leftPanel: { enabled: false, defaultOpen: false },
  rightPanel: { enabled: false, defaultOpen: false },
  bottomPanel: { enabled: false, defaultOpen: false }
}

interface StudioContainerProps {
  children: React.ReactNode
}

export function StudioContainer({ children }: StudioContainerProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  
  // Get most recent project for consistent rail navigation (client-side only)
  const [mostRecentProjectId, setMostRecentProjectId] = useState<string | null>(null)

  useEffect(() => {
    // Only run on client side after hydration to avoid SSR issues
    if (typeof window !== 'undefined') {
      try {
        const { getMostRecentProjectId } = useProjectState()
        setMostRecentProjectId(getMostRecentProjectId())
      } catch (error) {
        // TODO: Implement proper ProjectProvider integration to ensure last accessed 
        // project is consistently kept in memory across all routes. Currently this 
        // fails when ProjectStateProvider is not available in the component tree.
        console.debug('Could not get recent project:', error)
      }
    }
  }, []) // Empty dependency array - only run once after mount
  
  // Extract project ID from URL if we're in a specific project
  const projectId = pathname.match(/^\/studio\/([^\/]+)/)?.[1]
  
  // Determine current rail mode based on pathname
  const railMode: StudioRailMode = (() => {
    if (pathname === '/studio') return 'studio'
    if (pathname.includes('/devtools')) return 'devtools'
    if (pathname.includes('/settings')) return 'settings'
    if (pathname.includes('/component-gallery')) return 'component-gallery'
    if (pathname.includes('/series')) return 'series'
    if (pathname.includes('/articles')) return 'articles'
    if (projectId && pathname === `/studio/${projectId}`) return 'workspace'
    return projectId ? 'workspace' : 'studio' // default based on context
  })()
  
  // Get activity configuration based on current mode
  const activityConfig = railMode === 'workspace' ? EXPLORER_CONFIGURATION : TOOL_CONFIGURATION
  
  // Panel state management - initialize from activity config defaults
  const leftPanel = usePanelState(!activityConfig.leftPanel.defaultOpen)
  const rightPanel = usePanelState(!activityConfig.rightPanel.defaultOpen)
  const bottomPanel = usePanelState(!activityConfig.bottomPanel.defaultOpen)
  
  // Note: Project state management is handled by the individual project routes
  // that have ProjectStateProvider. We don't need it at this level.

  // Global keyboard shortcut for settings (⌘,)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey && event.key === ',') {
        event.preventDefault()
        setIsSettingsOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Navigation handler - navigate between different modes
  const handleRailNavigation = useCallback((mode: StudioRailMode) => {
    if (mode === 'studio') {
      router.push('/studio')
    } else if (mode === 'workspace' && projectId) {
      router.push(`/studio/${projectId}`)
    } else if (projectId) {
      router.push(`/studio/${projectId}/${mode}`)
    } else {
      // If we're not in a project context, navigate to studio first
      router.push('/studio')
    }
  }, [router, projectId])

  // Keyboard shortcuts - only enable for workspace mode
  useWorkspaceShortcuts({
    onToggleLeft: activityConfig.leftPanel.enabled ? leftPanel.toggle : undefined,
    onToggleRight: activityConfig.rightPanel.enabled ? rightPanel.toggle : undefined,
    onToggleBottom: activityConfig.bottomPanel.enabled ? bottomPanel.toggle : undefined
  })

  // Render content based on current rail mode
  const renderMainContent = () => {
    switch (railMode) {
      case 'studio':
        // Render the studio project list (passed as children)
        return children
        
      case 'devtools':
        return (
          <div className="h-full bg-background">
            <ToastProvider>
              <DevToolsPage onBackToProjects={() => {}} />
            </ToastProvider>
          </div>
        )
        
      case 'settings':
        return (
          <div className="h-full bg-background">
            <SettingsPage />
          </div>
        )
        
      case 'component-gallery':
        return <ComponentGallery />
        
      case 'series':
        return (
          <div className="h-full bg-background p-6">
            <div className="container mx-auto max-w-6xl">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-muted-foreground" />
                  <h1 className="text-2xl font-semibold">Series Management</h1>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Series
                </Button>
              </div>
              
              <div className="text-center py-16">
                <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h2 className="text-2xl font-semibold mb-2">Project Series</h2>
                <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                  Organize this project&apos;s stories into series and manage publishing workflows across multiple works.
                </p>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>✨ Create multi-book series within this project</p>
                  <p>📚 Track reading order and dependencies</p>
                  <p>🚀 Coordinate publishing schedules</p>
                  <p>📊 Analyze series performance</p>
                </div>
              </div>
            </div>
          </div>
        )
        
      case 'articles':
        return (
          <div className="h-full bg-background p-6">
            <div className="container mx-auto max-w-6xl">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <h1 className="text-2xl font-semibold">Articles & Publishing</h1>
                </div>
                <Button>
                  <Share2 className="h-4 w-4 mr-2" />
                  Publish Article
                </Button>
              </div>

              <div className="text-center py-16">
                <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h2 className="text-2xl font-semibold mb-2">Project Articles</h2>
                <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                  Manage published content for this project, share articles with readers, and track engagement.
                </p>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>📝 Publish articles and stories from this project</p>
                  <p>📖 Create public reading experiences</p>
                  <p>💬 Engage with your project&apos;s audience</p>
                  <p>📈 Track reader analytics and feedback</p>
                </div>
              </div>

              {/* Feature Cards */}
              <div className="grid md:grid-cols-3 gap-6 mt-12">
                <div className="border border-border rounded-lg p-6 text-center">
                  <Share2 className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Publishing</h3>
                  <p className="text-sm text-muted-foreground">
                    Share your finished works with readers across platforms.
                  </p>
                </div>
                
                <div className="border border-border rounded-lg p-6 text-center">
                  <Eye className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Analytics</h3>
                  <p className="text-sm text-muted-foreground">
                    Track views, engagement, and reader feedback for this project.
                  </p>
                </div>
                
                <div className="border border-border rounded-lg p-6 text-center">
                  <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Content Management</h3>
                  <p className="text-sm text-muted-foreground">
                    Organize and schedule publication of project content.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )
        
      case 'workspace':
      default:
        if (projectId) {
          return (
            <WorkspaceStateInitializer projectId={projectId} railMode={railMode as Exclude<RailMode, 'projects'>} pathname={pathname}>
              <WorkspaceLayout
                activityConfig={activityConfig}
                panelStates={{
                  leftPanel,
                  rightPanel,
                  bottomPanel
                }}
                railMode={railMode}
                projectId={projectId}
              />
            </WorkspaceStateInitializer>
          )
        }
        // If no projectId but we're in workspace mode, render children (fallback)
        return children
    }
  }

  return (
    <ProjectStateProvider>
      <TooltipProvider delayDuration={300}>
        <div className="h-screen bg-background flex overflow-hidden">
        {/* Studio Left Rail - Controls activity/mode */}
        <StudioLeftRail 
          activeMode={railMode}
          onModeChange={handleRailNavigation}
          onSettingsOpen={() => setIsSettingsOpen(true)}
          projectId={projectId}
          mostRecentProjectId={mostRecentProjectId}
          className="z-40"
        />

        {/* Main Content - Dynamically renders based on route */}
        <div className="flex-1 min-h-0 min-w-0">
          {renderMainContent()}
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
      </TooltipProvider>
    </ProjectStateProvider>
  )
}

// Initializes project-scoped state when viewing the workspace
function WorkspaceStateInitializer({
  projectId,
  railMode,
  pathname,
  children
}: {
  projectId: string
  railMode: RailMode
  pathname: string
  children: React.ReactNode
}) {
  const { switchToProject, updateActiveRoute } = useProjectState()

  useEffect(() => {
    switchToProject(projectId, { activeRailMode: railMode })
  }, [projectId, railMode, switchToProject])

  useEffect(() => {
    updateActiveRoute(projectId, pathname, railMode)
  }, [projectId, pathname, railMode, updateActiveRoute])

  return <>{children}</>
}