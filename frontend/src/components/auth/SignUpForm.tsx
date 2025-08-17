'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { AuthError } from './AuthError'
import { useAuth } from '@/contexts/AuthContext'
import { Github, Mail, Eye, EyeOff, CheckCircle2 } from 'lucide-react'
import { AuthError as SupabaseAuthError } from '@supabase/supabase-js'

const signUpSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string()
    .min(6, 'Password must be at least 6 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain at least one uppercase letter, one lowercase letter, and one number'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type SignUpData = z.infer<typeof signUpSchema>

interface SignUpFormProps {
  onModeChange: (mode: 'signin' | 'signup' | 'magic-link' | 'reset-password') => void
  onSuccess?: () => void
}

export function SignUpForm({ onModeChange, onSuccess }: SignUpFormProps) {
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState<SupabaseAuthError | null>(null)
  const [success, setSuccess] = useState(false)
  const { signUp, signInWithOAuth } = useAuth()

  const { register, handleSubmit, formState: { errors }, watch } = useForm<SignUpData>({
    resolver: zodResolver(signUpSchema),
  })

  const password = watch('password')

  const onSubmit = async (data: SignUpData) => {
    setLoading(true)
    setError(null)

    const { error } = await signUp(data.email, data.password)

    if (error) {
      setError(error)
      setLoading(false)
    } else {
      setSuccess(true)
      setLoading(false)
    }
  }

  const handleOAuthSignIn = async (provider: 'google' | 'github') => {
    setLoading(true)
    setError(null)

    const { error } = await signInWithOAuth(provider)

    if (error) {
      setError(error)
    }

    setLoading(false)
  }

  if (success) {
    return (
      <div className="text-center space-y-4">
        <div className="mx-auto w-12 h-12 bg-success/10 rounded-full flex items-center justify-center">
          <CheckCircle2 className="w-6 h-6 text-success" />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Check your email</h3>
          <p className="text-sm text-muted-foreground">
            We've sent you a confirmation link to complete your account setup.
          </p>
        </div>
        <Button
          onClick={() => onModeChange('signin')}
          variant="outline"
          className="w-full"
        >
          Back to Sign In
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <AuthError error={error} />

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
            <p className="text-sm text-destructive">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a password"
              {...register('password')}
              disabled={loading}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
              onClick={() => setShowPassword(!showPassword)}
              disabled={loading}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>
          {errors.password && (
            <p className="text-sm text-destructive">{errors.password.message}</p>
          )}
          {password && password.length > 0 && (
            <div className="text-xs text-muted-foreground space-y-1">
              <p className={password.length >= 6 ? 'text-success' : ''}>
                ✓ At least 6 characters
              </p>
              <p className={/[a-z]/.test(password) ? 'text-success' : ''}>
                ✓ One lowercase letter
              </p>
              <p className={/[A-Z]/.test(password) ? 'text-success' : ''}>
                ✓ One uppercase letter
              </p>
              <p className={/\d/.test(password) ? 'text-success' : ''}>
                ✓ One number
              </p>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              {...register('confirmPassword')}
              disabled={loading}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              disabled={loading}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>
          {errors.confirmPassword && (
            <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Creating account...' : 'Create Account'}
        </Button>
      </form>

      <Separator />

      <div className="space-y-2">
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleOAuthSignIn('google')}
          disabled={loading}
        >
          <Mail className="mr-2 h-4 w-4" />
          Continue with Google
        </Button>

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleOAuthSignIn('github')}
          disabled={loading}
        >
          <Github className="mr-2 h-4 w-4" />
          Continue with GitHub
        </Button>
      </div>

      <div className="text-center text-sm">
        Already have an account?{' '}
        <Button
          type="button"
          variant="link"
          className="p-0 h-auto font-semibold"
          onClick={() => onModeChange('signin')}
        >
          Sign in
        </Button>
      </div>
    </div>
  )
}