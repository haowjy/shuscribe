'use client'

import { useEffect, useState, type ComponentType } from 'react'
import { useRouter } from 'next/navigation'
import { 
  FolderOpen, 
  Palette, 
  Settings, 
  Database, 
  BookOpen, 
  FileText, 
  ChevronsLeft, 
  ChevronsRight, 
  Home,
  HelpCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import type { StudioRailMode } from './StudioContainer'

interface RailItem {
  id: StudioRailMode
  label: string
  icon: ComponentType<{ className?: string }>
  shortcut?: string
  disabled?: boolean
}

interface StudioLeftRailProps {
  activeMode: StudioRailMode
  onModeChange: (mode: StudioRailMode) => void
  onSettingsOpen: () => void
  projectId?: string
  mostRecentProjectId?: string | null
  className?: string
}

// Note: Global navigation items are handled individually in the component

// Workspace navigation item (shown in its own section)
const workspaceRailItem: RailItem = {
  id: 'workspace',
  label: 'Workspace',
  icon: FolderOpen,
  shortcut: '⌘B'
}

// Other project-specific navigation items
const projectRailItems: RailItem[] = [
  {
    id: 'series',
    label: 'Series',
    icon: BookOpen
  },
  {
    id: 'articles',
    label: 'Articles',
    icon: FileText
  }
]

// Development and utility tools
const toolsRailItems: RailItem[] = [
  {
    id: 'component-gallery',
    label: 'Component Gallery',
    icon: Palette
  },
  ...(process.env.NODE_ENV === 'development' ? [
    {
      id: 'devtools' as const,
      label: 'Developer Tools',
      icon: Database
    }
  ] : [])
]

export function StudioLeftRail({ 
  activeMode, 
  onModeChange, 
  onSettingsOpen, 
  projectId, 
  mostRecentProjectId,
  className 
}: StudioLeftRailProps) {

  const router = useRouter()
  
  // Persisted expand/collapse state (default collapsed)
  const STORAGE_KEY = 'shuscribe_ui_studio_rail_collapsed'
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved != null) {
        // stored value represents "collapsed"; invert for expanded
        setExpanded(saved !== 'true')
      }
    } catch {
      // ignore storage errors
    }
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, (!expanded).toString())
    } catch {
      // ignore storage errors
    }
  }, [expanded])

  const handleModeClick = (mode: StudioRailMode) => {
    // If we're on /studio and clicking a project-specific mode, navigate to recent project
    if (shouldGreyOut && mostRecentProjectId && (mode === 'workspace' || mode === 'series' || mode === 'articles')) {
      const targetPath = mode === 'workspace' 
        ? `/studio/${mostRecentProjectId}` 
        : `/studio/${mostRecentProjectId}/${mode}`
      router.push(targetPath)
    } else {
      // Normal mode change
      onModeChange(mode)
    }
  }


  const handleHelpClick = () => {
    // TODO: Implement help/documentation
    console.log('Help clicked')
  }

  const renderRailButton = (opts: {
    id?: StudioRailMode
    label: string
    icon: ComponentType<{ className?: string }>
    active?: boolean
    emphasis?: boolean
    onClick: () => void
    shortcut?: string
    disabled?: boolean
  }) => {
    const { label, icon: Icon, active, emphasis, onClick, shortcut, disabled } = opts
    const activeVariant: 'default' | 'secondary' | 'ghost' = emphasis
      ? (active ? 'default' : 'ghost')
      : (active ? 'secondary' : 'ghost')

    if (!expanded) {
      return (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={activeVariant}
              size="icon"
              className={cn(
                'h-8 w-8 flex-shrink-0 mx-auto', 
                !active && emphasis && 'text-primary',
                disabled && 'opacity-50'
              )}
              onClick={onClick}
              disabled={false}
              aria-label={label}
            >
              <Icon className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            <p>
              {label}
              {shortcut && <kbd className="ml-1 text-xs">{shortcut}</kbd>}
            </p>
          </TooltipContent>
        </Tooltip>
      )
    }

    return (
      <Button
        variant={activeVariant}
        size="sm"
        className={cn(
          'h-8 w-full justify-start gap-2 px-3 flex-shrink-0', 
          !active && emphasis && 'text-primary',
          disabled && 'opacity-50'
        )}
        onClick={onClick}
        disabled={false}
        aria-label={label}
      >
        <Icon className="h-3.5 w-3.5" />
        <span className="truncate">{label}</span>
        {shortcut && (
          <kbd className="ml-auto text-xs opacity-60">{shortcut}</kbd>
        )}
      </Button>
    )
  }

  // Always show project navigation for consistent rail structure
  const showProjectNavigation = true
  
  // Determine if project buttons should be greyed out (when not in a specific project)
  const isProjectContext = !!projectId
  const shouldGreyOut = !isProjectContext

  return (
    <TooltipProvider delayDuration={300}>
      <div className={cn(
        'flex flex-col bg-background border-r border-border h-full transition-[width] duration-200',
        expanded ? 'w-56' : 'w-12',
        className
      )}>
        {/* Expand / Collapse toggle */}
        <div className="p-1.5">
          {expanded ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-full justify-start gap-2"
              onClick={() => setExpanded(false)}
              aria-label="Collapse rail"
            >
              <ChevronsLeft className="h-3.5 w-3.5" />
              <span className="truncate">Collapse</span>
            </Button>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 mx-auto"
                  onClick={() => setExpanded(true)}
                  aria-label="Expand rail"
                >
                  <ChevronsRight className="h-3.5 w-3.5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Expand rail</p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        {/* Divider after collapse section */}
        <div className="h-px bg-border mx-2 my-1" />

        {/* Global Navigation Section */}
        <div className="flex flex-col gap-0.5 p-1.5">
          {/* Studio */}
          {renderRailButton({
            id: 'studio',
            label: 'Studio',
            icon: Home,
            active: activeMode === 'studio',
            onClick: () => handleModeClick('studio')
          })}

        </div>

        {/* Workspace Section (shown when in a project or have recent project) */}
        {showProjectNavigation && (
          <>
            <div className="h-px bg-border mx-2 my-1" />
            <div className="flex flex-col gap-0.5 p-1.5">
              {renderRailButton({
                id: workspaceRailItem.id,
                label: workspaceRailItem.label,
                icon: workspaceRailItem.icon,
                active: activeMode === workspaceRailItem.id,
                onClick: () => handleModeClick(workspaceRailItem.id),
                shortcut: workspaceRailItem.shortcut,
                disabled: shouldGreyOut
              })}
            </div>
          </>
        )}

        {/* Other Project Navigation (shown when in a project or have recent project) */}
        {showProjectNavigation && projectRailItems.length > 0 && (
          <>
            <div className="h-px bg-border mx-2 my-1" />
            <div className="flex flex-col gap-0.5 p-1.5">
            {projectRailItems.map((item) => (
              <div key={item.id}>
                {renderRailButton({
                  id: item.id,
                  label: item.label,
                  icon: item.icon,
                  active: activeMode === item.id,
                  onClick: () => handleModeClick(item.id),
                  shortcut: item.shortcut,
                  disabled: shouldGreyOut
                })}
              </div>
            ))}
            </div>
          </>
        )}

        {/* Spacer to push tools and settings to bottom */}
        <div className="flex-1" />

        {/* Tools Section */}
        {toolsRailItems.length > 0 && (
          <>
            <div className="h-px bg-border mx-2 my-1" />
            <div className="flex flex-col gap-0.5 p-1.5">
            {toolsRailItems.map((item) => (
              <div key={item.id}>
                {renderRailButton({
                  id: item.id,
                  label: item.label,
                  icon: item.icon,
                  active: activeMode === item.id,
                  onClick: () => handleModeClick(item.id)
                })}
              </div>
            ))}
            </div>
          </>
        )}

        {/* Settings Section */}
        <div className="h-px bg-border mx-2 my-1" />
        <div className="flex flex-col gap-0.5 p-1.5">
          {renderRailButton({
            label: 'Help',
            icon: HelpCircle,
            active: false,
            onClick: handleHelpClick
          })}
          
          {renderRailButton({
            id: 'settings',
            label: 'Settings',
            icon: Settings,
            active: activeMode === 'settings',
            onClick: () => onSettingsOpen(),
            shortcut: '⌘,'
          })}
        </div>
      </div>
    </TooltipProvider>
  )
}