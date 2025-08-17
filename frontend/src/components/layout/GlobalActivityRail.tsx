'use client'

import { useRouter } from 'next/navigation'
import { 
  Home, 
  Search, 
  Sparkles, 
  HelpCircle, 
  Settings,
  Database,
  Palette
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip'

interface GlobalActivityRailProps {
  onSettingsOpen: () => void
  onSearchFocus?: () => void
  onDevToolsClick?: () => void
  onComponentGalleryClick?: () => void
  onHomeClick?: () => void
  currentView?: 'projects' | 'devtools' | 'component-gallery'
  className?: string
}

export function GlobalActivityRail({ 
  onSettingsOpen, 
  onSearchFocus,
  onDevToolsClick,
  onComponentGalleryClick,
  onHomeClick,
  currentView = 'projects',
  className = '' 
}: GlobalActivityRailProps) {
  const router = useRouter()
  const showDevTools = process.env.NODE_ENV === 'development'

  const handleHomeClick = () => {
    if (onHomeClick) {
      onHomeClick()
    } else {
      // Fallback to routing if no callback provided
      router.push('/projects')
    }
  }

  const handleSearchClick = () => {
    if (onSearchFocus) {
      onSearchFocus()
    }
  }

  const handleAiClick = () => {
    // TODO: Implement AI assistant panel
    console.log('AI assistant clicked')
  }

  const handleHelpClick = () => {
    // TODO: Implement help/documentation
    console.log('Help clicked')
  }

  const handleDevToolsClick = () => {
    if (onDevToolsClick) {
      onDevToolsClick()
    }
  }

  const handleComponentGalleryClick = () => {
    if (onComponentGalleryClick) {
      onComponentGalleryClick()
    }
  }


  return (
    <TooltipProvider delayDuration={300}>
      {/* Desktop Rail */}
      <nav 
        className={`hidden md:flex fixed left-0 top-0 h-full w-14 bg-background border-r border-border flex-col items-center py-4 z-40 ${className}`}
        aria-label="Global navigation"
      >
        {/* Desktop rail content */}
        {/* Top Section - Navigation */}
        <div className="flex flex-col items-center space-y-3">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={currentView === 'projects' ? "secondary" : "ghost"}
                size="icon"
                className="h-9 w-9"
                onClick={handleHomeClick}
                aria-label="Home - Go to projects"
              >
                <Home className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Projects</p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={handleSearchClick}
                aria-label="Search projects and documents"
              >
                <Search className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Search</p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={handleAiClick}
                aria-label="AI Assistant"
              >
                <Sparkles className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>AI Assistant</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Developer Section - separated visually */}
        {showDevTools && (
          <div className="flex flex-col items-center mt-2">
            <div className="w-8 h-px bg-border my-2" />
            <div className="flex flex-col items-center space-y-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={currentView === 'component-gallery' ? "secondary" : "ghost"}
                    size="icon"
                    className="h-9 w-9"
                    onClick={handleComponentGalleryClick}
                    aria-label="Component Gallery"
                  >
                    <Palette className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>Component Gallery</p>
                </TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={currentView === 'devtools' ? "secondary" : "ghost"}
                    size="icon"
                    className="h-9 w-9"
                    onClick={handleDevToolsClick}
                    aria-label="Developer Tools"
                  >
                    <Database className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p>Developer Tools</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Bottom Section - Settings & Help */}
        <div className="flex flex-col items-center space-y-3">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={handleHelpClick}
                aria-label="Help and support"
              >
                <HelpCircle className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Help</p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={onSettingsOpen}
                aria-label="Settings and account"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Settings <kbd className="ml-1 text-xs">⌘,</kbd></p>
            </TooltipContent>
          </Tooltip>
        </div>
      </nav>

      {/* Mobile Floating Dock */}
      <nav 
        className={`md:hidden fixed bottom-6 right-6 bg-background border border-border rounded-2xl shadow-lg flex items-center gap-1 p-2 z-40 pb-[env(safe-area-inset-bottom)] pr-[env(safe-area-inset-right)] ${className}`}
        aria-label="Global navigation"
      >
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={currentView === 'projects' ? "secondary" : "ghost"}
              size="icon"
              className="h-8 w-8"
              onClick={handleHomeClick}
              aria-label="Home - Go to projects"
            >
              <Home className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Projects</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={handleSearchClick}
              aria-label="Search projects and documents"
            >
              <Search className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Search</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={handleAiClick}
              aria-label="AI Assistant"
            >
              <Sparkles className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>AI Assistant</p>
          </TooltipContent>
        </Tooltip>

        {showDevTools && (
          <>
            <div className="w-px h-6 bg-border mx-1" />

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={currentView === 'component-gallery' ? "secondary" : "ghost"}
                  size="icon"
                  className="h-8 w-8"
                  onClick={handleComponentGalleryClick}
                  aria-label="Component Gallery"
                >
                  <Palette className="h-3.5 w-3.5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p>Component Gallery</p>
              </TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={currentView === 'devtools' ? "secondary" : "ghost"}
                  size="icon"
                  className="h-8 w-8"
                  onClick={handleDevToolsClick}
                  aria-label="Developer Tools"
                >
                  <Database className="h-3.5 w-3.5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p>Developer Tools</p>
              </TooltipContent>
            </Tooltip>
          </>
        )}

        <div className="w-px h-6 bg-border mx-1" />

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={handleHelpClick}
              aria-label="Help and support"
            >
              <HelpCircle className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Help</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onSettingsOpen}
              aria-label="Settings and account"
            >
              <Settings className="h-3.5 w-3.5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Settings</p>
          </TooltipContent>
        </Tooltip>
      </nav>
    </TooltipProvider>
  )
}