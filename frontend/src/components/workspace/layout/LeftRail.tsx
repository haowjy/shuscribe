'use client'

import { useEffect, useState, type ComponentType } from 'react'
import { useRouter } from 'next/navigation'
import { FolderOpen, Palette, Settings, Database, BookOpen, FileText, ChevronsLeft, ChevronsRight, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import type { RailMode, RailItem, LeftRailProps } from './types'

// Main workspace activities
const mainRailItems: RailItem[] = [
  {
    id: 'workspace',
    label: 'Files',
    icon: FolderOpen,
    shortcut: '⌘B'
  },
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

// Settings and configuration
const settingsRailItems: RailItem[] = [
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    shortcut: '⌘,'
  }
]

export function LeftRail({ activeMode, onModeChange, className }: LeftRailProps) {
  const router = useRouter()

  // Persisted expand/collapse state (default collapsed)
  const STORAGE_KEY = 'shuscribe_ui_left_rail_collapsed'
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, (!expanded).toString())
    } catch {
      // ignore storage errors
    }
  }, [expanded])

  const handleModeClick = (mode: RailMode) => {
    onModeChange(mode)
  }

  const handleGoToProjects = () => {
    router.push('/projects')
  }

  const renderRailButton = (
    opts: {
      id?: string
      label: string
      icon: ComponentType<{ className?: string }>
      active?: boolean
      emphasis?: boolean
      onClick: () => void
    }
  ) => {
    const { label, icon: Icon, active, emphasis, onClick } = opts
    const activeVariant: 'default' | 'secondary' | 'ghost' = emphasis
      ? (active ? 'default' : 'ghost')
      : (active ? 'secondary' : 'ghost')
    if (!expanded) {
      return (
        <Button
          variant={activeVariant}
          size="icon"
          className={cn('h-10 w-10 flex-shrink-0 mx-auto', !active && emphasis && 'text-primary')}
          onClick={onClick}
          aria-label={label}
        >
          <Icon className="h-4 w-4" />
        </Button>
      )
    }
    return (
      <Button
        variant={activeVariant}
        size="sm"
        className={cn('h-10 w-full justify-start gap-2 px-3 flex-shrink-0', !active && emphasis && 'text-primary')}
        onClick={onClick}
        aria-label={label}
      >
        <Icon className="h-4 w-4" />
        <span className="truncate">{label}</span>
      </Button>
    )
  }

  return (
    <TooltipProvider delayDuration={300}>
      <div className={cn(
        'flex flex-col bg-background border-r border-border h-full transition-[width] duration-200',
        expanded ? 'w-56' : 'w-14',
        className
      )}>
        {/* Expand / Collapse toggle */}
        <div className="p-2 border-b border-border">
          {expanded ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-9 w-full justify-start gap-2"
              onClick={() => setExpanded(false)}
              aria-label="Collapse rail"
            >
              <ChevronsLeft className="h-4 w-4" />
              <span className="truncate">Collapse</span>
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-10 mx-auto"
              onClick={() => setExpanded(true)}
              aria-label="Expand rail"
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Back to projects selector */}
        <div className="flex flex-col gap-1 p-2">
          <Tooltip>
            <TooltipTrigger asChild>
              {renderRailButton({
                label: 'Projects',
                icon: Home,
                active: false,
                onClick: handleGoToProjects
              })}
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Back to Projects</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Main Activities Section */}
        <div className="flex flex-col gap-1 p-2">
          {mainRailItems.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                {renderRailButton({
                  id: item.id,
                  label: item.label,
                  icon: item.icon,
                  active: activeMode === item.id,
                  emphasis: item.id === 'workspace',
                  onClick: () => handleModeClick(item.id)
                })}
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>
                  {item.label}
                  {item.shortcut && ` ${item.shortcut}`}
                </p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>

        {/* Spacer to push tools and settings to bottom */}
        <div className="flex-1" />

        {/* Tools Section */}
        {toolsRailItems.length > 0 && (
          <div className="flex flex-col gap-1 p-2 border-t border-border">
            {toolsRailItems.map((item) => (
              <Tooltip key={item.id}>
                <TooltipTrigger asChild>
                  {renderRailButton({
                    id: item.id,
                    label: item.label,
                    icon: item.icon,
                    active: activeMode === item.id,
                    onClick: () => handleModeClick(item.id)
                  })}
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>{item.label}</p>
                </TooltipContent>
              </Tooltip>
            ))}
          </div>
        )}

        {/* Settings Section */}
        <div className="flex flex-col gap-1 p-2 border-t border-border">
          {settingsRailItems.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                {renderRailButton({
                  id: item.id,
                  label: item.label,
                  icon: item.icon,
                  active: activeMode === item.id,
                  onClick: () => handleModeClick(item.id)
                })}
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>
                  {item.label}
                  {item.shortcut && ` ${item.shortcut}`}
                </p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>
    </TooltipProvider>
  )
}

// Re-export types for convenience
export type { RailMode, RailItem, LeftRailProps } from './types'