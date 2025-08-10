import { useAuth } from '@/contexts/AuthContext'

export function useUser() {
  const { user, loading } = useAuth()
  
  return {
    user,
    loading,
    isAuthenticated: !!user,
    userId: user?.id,
    userEmail: user?.email,
    userMetadata: user?.user_metadata,
  }
}