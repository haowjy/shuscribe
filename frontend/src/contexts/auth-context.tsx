"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { User, Session } from "@supabase/supabase-js";
import { useQueryClient } from "@tanstack/react-query";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const queryClient = useQueryClient();

  // Sync Supabase session with localStorage for API client
  const syncAuthToLocalStorage = (session: Session | null) => {
    if (typeof window === 'undefined') return;
    
    if (session?.access_token) {
      // Store token for API client
      localStorage.setItem('shuscribe_auth', JSON.stringify({
        token: session.access_token,
        userId: session.user.id,
        email: session.user.email
      }));
    } else {
      // Clear auth data on logout
      localStorage.removeItem('shuscribe_auth');
    }
  };

  useEffect(() => {
    const supabase = createClient();

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      syncAuthToLocalStorage(session);
      setLoading(false);
    });

    // Listen for changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      syncAuthToLocalStorage(session);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    const supabase = createClient();
    
    // Clear Supabase session
    await supabase.auth.signOut();
    
    // Clear localStorage auth data (handled by syncAuthToLocalStorage)
    // but explicitly clear to be sure
    if (typeof window !== 'undefined') {
      localStorage.removeItem('shuscribe_auth');
    }
    
    // Clear TanStack Query cache to prevent stale authenticated requests
    queryClient.clear();
    
    // Force redirect to login page
    window.location.href = '/auth/login';
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}