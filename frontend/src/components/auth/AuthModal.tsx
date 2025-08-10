'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { SignInForm } from './SignInForm'
import { SignUpForm } from './SignUpForm'
import { MagicLinkForm } from './MagicLinkForm'
import { ResetPasswordForm } from './ResetPasswordForm'

type AuthMode = 'signin' | 'signup' | 'magic-link' | 'reset-password'

interface AuthModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultMode?: AuthMode
}

export function AuthModal({ open, onOpenChange, defaultMode = 'signin' }: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>(defaultMode)

  const titles = {
    signin: 'Sign In to ShuScribe',
    signup: 'Create Your Account',
    'magic-link': 'Sign In with Magic Link',
    'reset-password': 'Reset Your Password',
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{titles[mode]}</DialogTitle>
        </DialogHeader>

        {mode === 'signin' && (
          <SignInForm
            onModeChange={setMode}
            onSuccess={() => onOpenChange(false)}
          />
        )}

        {mode === 'signup' && (
          <SignUpForm
            onModeChange={setMode}
            onSuccess={() => onOpenChange(false)}
          />
        )}

        {mode === 'magic-link' && (
          <MagicLinkForm
            onModeChange={setMode}
            onSuccess={() => onOpenChange(false)}
          />
        )}

        {mode === 'reset-password' && (
          <ResetPasswordForm
            onModeChange={setMode}
            onSuccess={() => onOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}