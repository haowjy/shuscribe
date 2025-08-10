import { AuthError as SupabaseAuthError } from '@supabase/supabase-js'
import { AlertCircle } from 'lucide-react'

interface AuthErrorProps {
  error: SupabaseAuthError | null
}

export function AuthError({ error }: AuthErrorProps) {
  if (!error) return null

  const getErrorMessage = (error: SupabaseAuthError) => {
    switch (error.message) {
      case 'Invalid login credentials':
        return 'Invalid email or password. Please check your credentials and try again.'
      case 'User not found':
        return 'No account found with this email address.'
      case 'Email not confirmed':
        return 'Please check your email and click the confirmation link before signing in.'
      case 'Password should be at least 6 characters':
        return 'Password must be at least 6 characters long.'
      case 'Unable to validate email address: invalid format':
        return 'Please enter a valid email address.'
      default:
        return error.message || 'An unexpected error occurred. Please try again.'
    }
  }

  return (
    <div className="flex items-center gap-2 p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
      <AlertCircle size={16} />
      <span>{getErrorMessage(error)}</span>
    </div>
  )
}