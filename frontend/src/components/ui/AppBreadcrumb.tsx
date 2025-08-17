'use client'

import * as React from 'react'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'

export interface BreadcrumbItemData {
  label: string | React.ReactNode
  onClick?: () => void
  isActive?: boolean
}

interface AppBreadcrumbProps {
  items: BreadcrumbItemData[]
  className?: string
}

export function AppBreadcrumb({ items, className }: AppBreadcrumbProps) {
  if (items.length === 0) return null

  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        {items.map((item, index) => (
          <React.Fragment key={index}>
            <BreadcrumbItem>
              {item.isActive ? (
                <BreadcrumbPage className="text-foreground font-semibold px-2 py-0.5">
                  {item.label}
                </BreadcrumbPage>
              ) : (
                <BreadcrumbLink asChild>
                  <button
                    onClick={item.onClick}
                    className="text-foreground hover:text-primary hover:underline transition-colors cursor-pointer font-semibold px-2 py-0.5 rounded-sm hover:bg-accent/50"
                  >
                    {item.label}
                  </button>
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
            {index < items.length - 1 && (
              <BreadcrumbSeparator />
            )}
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  )
}