'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { AuthError } from './AuthError'
import { useAuth } from '@/contexts/AuthContext'
import { Mail, CheckCircle2, ArrowLeft } from 'lucide-react'
import { AuthError as SupabaseAuthError } from '@supabase/supabase-js'

const magicLinkSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type MagicLinkData = z.infer<typeof magicLinkSchema>

interface MagicLinkFormProps {
  onModeChange: (mode: 'signin' | 'signup' | 'magic-link' | 'reset-password') => void
  onSuccess?: () => void
}

export function MagicLinkForm({ onModeChange, onSuccess }: MagicLinkFormProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<SupabaseAuthError | null>(null)
  const [success, setSuccess] = useState(false)
  const { sendMagicLink } = useAuth()

  const { register, handleSubmit, formState: { errors } } = useForm<MagicLinkData>({
    resolver: zodResolver(magicLinkSchema),
  })

  const onSubmit = async (data: MagicLinkData) => {
    setLoading(true)
    setError(null)

    const { error } = await sendMagicLink(data.email)

    if (error) {
      setError(error)
      setLoading(false)
    } else {
      setSuccess(true)
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="text-center space-y-4">
        <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <CheckCircle2 className="w-6 h-6 text-blue-600" />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Check your email</h3>
          <p className="text-sm text-muted-foreground">
            We've sent you a magic link to sign in to your account.
          </p>
        </div>
        <Button
          onClick={() => onModeChange('signin')}
          variant="outline"
          className="w-full"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Sign In
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <AuthError error={error} />

      <div className="text-center space-y-2">
        <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <Mail className="w-6 h-6 text-blue-600" />
        </div>
        <p className="text-sm text-muted-foreground">
          Enter your email address and we'll send you a magic link to sign in.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="Enter your email"
            {...register('email')}
            disabled={loading}
          />
          {errors.email && (
            <p className="text-sm text-red-600">{errors.email.message}</p>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Sending...' : 'Send Magic Link'}
        </Button>
      </form>

      <div className="text-center">
        <Button
          type="button"
          variant="link"
          className="text-sm"
          onClick={() => onModeChange('signin')}
        >
          <ArrowLeft className="mr-1 h-3 w-3" />
          Back to Sign In
        </Button>
      </div>
    </div>
  )
}