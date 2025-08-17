'use client'

import { Settings, User, Database, BookOpen } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip'
import { AppBreadcrumb, type BreadcrumbItemData } from '@/components/ui/AppBreadcrumb'

interface ProjectsHeaderProps {
  onSettingsClick: () => void
  onProfileClick?: () => void
  onDevToolsClick?: () => void
  onBackToProjects?: () => void
  currentView?: 'projects' | 'devtools'
}

export function ProjectsHeader({
  onSettingsClick,
  onProfileClick,
  onDevToolsClick,
  onBackToProjects,
  currentView = 'projects'
}: ProjectsHeaderProps) {
  const showDevTools = process.env.NODE_ENV === 'development'

  const handleProfileClick = () => {
    if (onProfileClick) {
      onProfileClick()
    } else {
      // TODO: Implement profile functionality
      console.log('Profile clicked')
    }
  }

  // Build breadcrumb items based on current view
  const breadcrumbItems: BreadcrumbItemData[] = [
    {
      label: 'ShuScribe',
      onClick: onBackToProjects
    },
    ...(currentView === 'devtools' ? [{
      label: 'Developer Tools',
      onClick: () => {}, // Stay in current view for consistency
      isActive: true
    }] : [])
  ]

  return (
    <TooltipProvider delayDuration={300}>
      <header className="flex h-12 items-center justify-between border-b border-border bg-background px-6">
        {/* Left: Breadcrumb Navigation */}
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          <AppBreadcrumb items={breadcrumbItems} />
        </div>

        {/* Right: Action Buttons */}
        <div className="flex items-center gap-1">
          {/* DevTools (development only) */}
          {showDevTools && onDevToolsClick && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={currentView === 'devtools' ? 'secondary' : 'ghost'}
                  size="icon"
                  className="h-8 w-8"
                  onClick={onDevToolsClick}
                  aria-label="Open developer tools"
                >
                  <Database className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <p>Developer Tools</p>
              </TooltipContent>
            </Tooltip>
          )}

          {/* Profile */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={handleProfileClick}
                aria-label="Profile"
              >
                <User className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>Profile</p>
            </TooltipContent>
          </Tooltip>

          {/* Settings */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={onSettingsClick}
                aria-label="Open settings"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <p>Settings ⌘,</p>
            </TooltipContent>
          </Tooltip>
        </div>
      </header>
    </TooltipProvider>
  )
}