'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useAuth } from '@/contexts/AuthContext'
import { useUser } from '@/hooks/useUser'
import {
  User,
  LogOut,
  Palette,
  Keyboard,
  HelpCircle,
  Settings
} from 'lucide-react'

export function SettingsPage() {
  const { user } = useUser()
  const { signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  if (!user) return null

  return (
    <div className="h-full bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <Settings className="h-5 w-5 text-muted-foreground" />
            <div>
              <h1 className="text-xl font-semibold">Settings</h1>
              <p className="text-sm text-muted-foreground">
                Manage your account settings and preferences
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-2xl mx-auto space-y-8">
          {/* Account Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Account</h3>
            </div>
            
            <div className="pl-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-primary-foreground" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-lg font-medium truncate">
                    {user.email?.split('@')[0] || 'User'}
                  </span>
                  <span className="text-sm text-muted-foreground truncate">
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
            
            <div className="pl-6 space-y-3">
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
            
            <div className="pl-6 space-y-3">
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
              className="text-destructive hover:bg-destructive/10 flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}