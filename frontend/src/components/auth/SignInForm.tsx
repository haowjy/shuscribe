'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { AuthError } from './AuthError'
import { useAuth } from '@/contexts/AuthContext'
import { Github, Mail, Eye, EyeOff } from 'lucide-react'
import { AuthError as SupabaseAuthError } from '@supabase/supabase-js'

const signInSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type SignInData = z.infer<typeof signInSchema>

interface SignInFormProps {
  onModeChange: (mode: 'signin' | 'signup' | 'magic-link' | 'reset-password') => void
  onSuccess: () => void
}

export function SignInForm({ onModeChange, onSuccess }: SignInFormProps) {
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<SupabaseAuthError | null>(null)
  const { signIn, signInWithOAuth } = useAuth()
  const router = useRouter()

  const { register, handleSubmit, formState: { errors } } = useForm<SignInData>({
    resolver: zodResolver(signInSchema),
  })

  const onSubmit = async (data: SignInData) => {
    setLoading(true)
    setError(null)

    const { error } = await signIn(data.email, data.password)

    if (error) {
      setError(error)
      setLoading(false)
    } else {
      onSuccess()
      router.push('/projects')
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
              placeholder="Enter your password"
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
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>

      <div className="text-center">
        <Button
          type="button"
          variant="link"
          className="text-sm"
          onClick={() => onModeChange('reset-password')}
        >
          Forgot your password?
        </Button>
      </div>

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

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => onModeChange('magic-link')}
          disabled={loading}
        >
          <Mail className="mr-2 h-4 w-4" />
          Send Magic Link
        </Button>
      </div>

      <div className="text-center text-sm">
        Don't have an account?{' '}
        <Button
          type="button"
          variant="link"
          className="p-0 h-auto font-semibold"
          onClick={() => onModeChange('signup')}
        >
          Sign up
        </Button>
      </div>
    </div>
  )
}