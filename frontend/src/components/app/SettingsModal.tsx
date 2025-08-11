'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useAuth } from '@/contexts/AuthContext'
import { useUser } from '@/hooks/useUser'
import {
  User,
  LogOut,
  Palette,
  Keyboard,
  HelpCircle
} from 'lucide-react'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { user } = useUser()
  const { signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    onClose()
    router.push('/')
  }
  

  // Keyboard shortcut support (⌘,)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey && event.key === ',') {
        event.preventDefault()
        if (!isOpen) {
          // This will be handled by the parent component
          // The parent should listen for this combination and open the modal
        }
      }
      if (event.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!user) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Manage your account settings and preferences
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Account Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Account</h3>
            </div>
            
            <div className="pl-6 space-y-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-primary-foreground" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-sm font-medium truncate">
                    {user.email?.split('@')[0] || 'User'}
                  </span>
                  <span className="text-xs text-muted-foreground truncate">
                    {user.email}
                  </span>
                </div>
              </div>
              
              <Button variant="outline" size="sm" className="w-fit">
                Edit Profile
              </Button>
            </div>
          </div>

          <Separator />

          {/* Preferences Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Palette className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Preferences</h3>
            </div>
            
            <div className="pl-6 space-y-2">
              <Button variant="outline" size="sm" className="w-fit">
                Theme Settings
              </Button>
              <Button variant="outline" size="sm" className="w-fit flex items-center gap-2">
                <Keyboard className="h-3 w-3" />
                Keyboard Shortcuts
              </Button>
            </div>
          </div>

          <Separator />

          {/* Help Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <HelpCircle className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Help & Support</h3>
            </div>
            
            <div className="pl-6 space-y-2">
              <Button variant="outline" size="sm" className="w-fit">
                Documentation
              </Button>
              <Button variant="outline" size="sm" className="w-fit">
                Contact Support
              </Button>
            </div>
          </div>

          <Separator />

          {/* Sign Out */}
          <div className="flex justify-start">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleSignOut}
              className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}