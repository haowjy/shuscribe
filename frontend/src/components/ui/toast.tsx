'use client'

import { X, CheckCircle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './button'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'info'
  title: string
  description?: string
  duration?: number
}

interface ToastProps {
  toast: Toast
  onClose: (id: string) => void
}

export function ToastComponent({ toast, onClose }: ToastProps) {
  const { id, type, title, description } = toast

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: AlertCircle
  }

  const styles = {
    success: 'bg-success/10 border-success/30 text-success',
    error: 'bg-destructive/10 border-destructive/30 text-destructive',
    info: 'bg-info/10 border-info/30 text-info'
  }

  const Icon = icons[type]

  return (
    <div
      className={cn(
        "flex items-start gap-3 p-4 rounded-lg border shadow-lg max-w-md w-full",
        "motion-reduce:animate-none motion-reduce:transition-none animate-in slide-in-from-right-full duration-300",
        styles[type]
      )}
    >
      <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
      
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm">{title}</p>
        {description && (
          <p className="text-sm opacity-90 mt-1">{description}</p>
        )}
      </div>

      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 opacity-70 hover:opacity-100"
        onClick={() => onClose(id)}
      >
        <X className="h-3 w-3" />
      </Button>
    </div>
  )
}

interface ToasterProps {
  toasts: Toast[]
  onClose: (id: string) => void
}

export function Toaster({ toasts, onClose }: ToasterProps) {
  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-md">
      {toasts.map((toast) => (
        <ToastComponent key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  )
}