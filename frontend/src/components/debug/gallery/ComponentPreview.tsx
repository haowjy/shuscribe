'use client'

import React, { useState, createElement, useEffect, useRef } from 'react'
import { Copy, Check, ChevronDown, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { getComponentById, getVariantById, ComponentDefinition, ComponentVariant } from './galleryConfig'

interface ComponentPreviewProps {
  componentId: string
  variantId: string
  viewMode: 'preview' | 'code'
}

interface CodeBlockProps {
  code: string
  language?: string
}

function CodeBlock({ code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const codeRef = useRef<HTMLPreElement>(null)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy code:', err)
    }
  }

  // Determine if code needs vertical scrolling (more than 20 lines)
  const codeLines = code.split('\n').length
  const needsVerticalScroll = codeLines > 20

  return (
    <div className="relative group">
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 h-8 w-8 p-0 z-10 opacity-60 group-hover:opacity-100 transition-opacity bg-muted/80 hover:bg-muted"
        onClick={handleCopy}
      >
        {copied ? (
          <Check className="h-3 w-3" />
        ) : (
          <Copy className="h-3 w-3" />
        )}
      </Button>
      <pre 
        ref={codeRef}
        className={`bg-muted rounded-lg p-4 text-sm overflow-auto scroll-smooth ${
          needsVerticalScroll ? 'max-h-96' : ''
        }`}
      >
        <code className="text-muted-foreground whitespace-pre">{code}</code>
      </pre>
      
      {/* Scroll indicators */}
      {needsVerticalScroll && (
        <div className="absolute bottom-2 right-2 text-xs text-muted-foreground opacity-60 pointer-events-none">
          ↕ Scroll
        </div>
      )}
    </div>
  )
}

interface ComponentDemoDisplayProps {
  component: ComponentDefinition
  variant: ComponentVariant
}

function ComponentDemoDisplay({ component, variant }: ComponentDemoDisplayProps) {
  try {
    // Special handling for complex components that need custom children
    if (variant.props.hasChildren) {
      // Handle Card components with custom layouts
      if (component.id === 'card') {
        if (variant.id === 'basic') {
          return (
            <div className="p-8 bg-background border rounded-lg">
              <Card>
                <CardHeader>
                  <CardTitle>Card Title</CardTitle>
                  <CardDescription>Card description goes here</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>This is the main content of the card.</p>
                </CardContent>
              </Card>
            </div>
          )
        }
        if (variant.id === 'with-footer') {
          return (
            <div className="p-8 bg-background border rounded-lg">
              <Card>
                <CardHeader>
                  <CardTitle>Project Overview</CardTitle>
                  <CardDescription>Manage your writing project</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>Track your progress, manage chapters, and collaborate with others.</p>
                </CardContent>
                <CardFooter className="gap-2">
                  <Button variant="outline" size="sm">Cancel</Button>
                  <Button size="sm">Save Changes</Button>
                </CardFooter>
              </Card>
            </div>
          )
        }
      }
      
      // Handle Input with label
      if (component.id === 'input' && variant.id === 'with-label') {
        return (
          <div className="p-8 bg-background border rounded-lg">
            <div className="space-y-2 max-w-sm">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="Enter your email" />
            </div>
          </div>
        )
      }

      // Handle EditorTabs component
      if (component.id === 'editor-tabs') {
        const handleTabSelect = (tabId: string) => console.log('Tab selected:', tabId)
        const handleTabClose = (tabId: string) => console.log('Tab closed:', tabId)
        const handleNewTab = () => console.log('New tab requested')
        const handleReorderTabs = (fromIndex: number, toIndex: number) => 
          console.log('Reorder tabs:', fromIndex, '->', toIndex)

        return (
          <div className="bg-background border rounded-lg">
            <div className="h-12 border-b">
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {createElement(component.component as React.ComponentType<any>, {
                ...variant.props,
                onTabSelect: handleTabSelect,
                onTabClose: handleTabClose,
                onNewTab: handleNewTab,
                onReorderTabs: handleReorderTabs
              })}
            </div>
            <div className="p-4 text-center text-sm text-muted-foreground">
              Tab content area would appear here
            </div>
          </div>
        )
      }

      // Handle AI Chat component
      if (component.id === 'ai-chat') {
        const handleUpdateMessages = (messages: unknown[]) => console.log('Messages updated:', messages)
        const handleNewThread = () => console.log('New thread requested')

        return (
          <div className="bg-background border rounded-lg h-[500px]">
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {createElement(component.component as React.ComponentType<any>, {
              ...variant.props,
              onUpdateMessages: handleUpdateMessages,
              onNewThread: handleNewThread
            })}
          </div>
        )
      }

      // Handle File Explorer component
      if (component.id === 'file-explorer') {
        return (
          <div className="bg-background border rounded-lg h-[400px] w-[300px]">
            {createElement(component.component, variant.props)}
          </div>
        )
      }

      // Handle Dialog component
      if (component.id === 'dialog') {
        // Dialog needs special handling for preview - render as a static mockup
        return (
          <div className="p-8 bg-background border rounded-lg">
            <div className="space-y-4">
              <div className="text-sm text-muted-foreground mb-4">
                Dialog Preview (Click button to see actual behavior)
              </div>
              {variant.id === 'basic' && (
                <div className="space-y-4">
                  <Button>Open Dialog</Button>
                  <div className="border rounded-lg p-4 bg-muted/10">
                    <h3 className="font-semibold mb-2">Dialog Title</h3>
                    <p className="text-sm text-muted-foreground mb-4">This is a basic dialog description explaining what this modal is for.</p>
                    <p className="mb-4">Dialog content goes here.</p>
                    <div className="flex gap-2 justify-end">
                      <Button variant="outline" size="sm">Cancel</Button>
                      <Button size="sm">Confirm</Button>
                    </div>
                  </div>
                </div>
              )}
              {variant.id === 'form-dialog' && (
                <div className="space-y-4">
                  <Button>Create Project</Button>
                  <div className="border rounded-lg p-4 bg-muted/10">
                    <h3 className="font-semibold mb-2">Create New Project</h3>
                    <p className="text-sm text-muted-foreground mb-4">Enter the details for your new writing project.</p>
                    <div className="space-y-2 mb-4">
                      <Input placeholder="My Amazing Story" />
                      <Input placeholder="A brief description..." />
                    </div>
                    <div className="flex gap-2 justify-end">
                      <Button variant="outline" size="sm">Cancel</Button>
                      <Button size="sm">Create Project</Button>
                    </div>
                  </div>
                </div>
              )}
              {variant.id === 'confirmation' && (
                <div className="space-y-4">
                  <Button variant="destructive">Delete Project</Button>
                  <div className="border rounded-lg p-4 bg-muted/10">
                    <h3 className="font-semibold mb-2">Delete Project</h3>
                    <p className="text-sm text-muted-foreground mb-4">This action cannot be undone. This will permanently delete your project and all associated files.</p>
                    <div className="flex gap-2 justify-end">
                      <Button variant="outline" size="sm">Cancel</Button>
                      <Button variant="destructive" size="sm">Delete Project</Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      }

      // Handle DropdownMenu component
      if (component.id === 'dropdown-menu') {
        return (
          <div className="p-8 bg-background border rounded-lg">
            <div className="text-sm text-muted-foreground mb-4">
              Dropdown Menu Preview (Interactive in live site)
            </div>
            {createElement(component.component, variant.props)}
          </div>
        )
      }

      // Handle ResizablePanel component
      if (component.id === 'resizable-panel') {
        if (variant.id === 'horizontal') {
          return (
            <div className="bg-background border rounded-lg p-4">
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {createElement(component.component as React.ComponentType<any>, {
                direction: 'horizontal',
                className: 'h-[200px] border rounded-lg'
              }, [
                createElement('div', { key: 'panel1', className: 'p-4 bg-muted/30' }, 'Left Panel'),
                createElement('div', { key: 'handle1', className: 'w-1 bg-border' }),
                createElement('div', { key: 'panel2', className: 'p-4' }, 'Right Panel')
              ])}
            </div>
          )
        }
        if (variant.id === 'vertical') {
          return (
            <div className="bg-background border rounded-lg p-4">
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {createElement(component.component as React.ComponentType<any>, {
                direction: 'vertical',
                className: 'h-[300px] border rounded-lg'
              }, [
                createElement('div', { key: 'panel1', className: 'p-4 bg-muted/30' }, 'Top Panel'),
                createElement('div', { key: 'handle1', className: 'h-1 bg-border' }),
                createElement('div', { key: 'panel2', className: 'p-4' }, 'Bottom Panel')
              ])}
            </div>
          )
        }
        if (variant.id === 'three-panel') {
          return (
            <div className="bg-background border rounded-lg p-4">
              <div className="h-[250px] border rounded-lg bg-muted/10 p-2">
                <div className="flex h-full gap-1">
                  <div className="w-1/4 bg-muted/30 rounded p-2 text-xs">Sidebar</div>
                  <div className="flex-1 flex flex-col gap-1">
                    <div className="flex-1 bg-background rounded p-2 text-xs">Main Content</div>
                    <div className="h-1/3 bg-muted/20 rounded p-2 text-xs">Bottom Panel</div>
                  </div>
                  <div className="w-1/4 bg-muted/30 rounded p-2 text-xs">Right Panel</div>
                </div>
              </div>
            </div>
          )
        }
      }
    }

    // Full-width rendering for editor components
    if (component.id === 'document-editor') {
      return (
        <div className="bg-background border rounded-lg min-h-[400px]">
          {createElement(component.component, variant.props)}
        </div>
      )
    }

    // Standard component rendering for small UI components (centered)
    return (
      <div className="p-8 bg-background border rounded-lg flex items-center justify-center min-h-[200px]">
        {createElement(component.component, variant.props)}
      </div>
    )
  } catch {
    return (
      <div className="p-8 bg-background border rounded-lg flex items-center justify-center min-h-[200px] text-muted-foreground">
        <div className="text-center">
          <div className="text-sm font-medium mb-1">Preview Error</div>
          <div className="text-xs">Failed to render component</div>
        </div>
      </div>
    )
  }
}

export function ComponentPreview({ 
  componentId, 
  variantId, 
  viewMode 
}: ComponentPreviewProps) {
  const [propsExpanded, setPropsExpanded] = useState(false)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  
  const component = getComponentById(componentId)
  const variant = component ? getVariantById(componentId, variantId) : undefined

  // Scroll to top when component or variant changes
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [componentId, variantId])

  // Scroll to top when view mode changes
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [viewMode])

  if (!component || !variant) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <div className="text-lg font-medium mb-2">No Component Selected</div>
          <div className="text-sm">Choose a component from the sidebar to see its preview</div>
        </div>
      </div>
    )
  }

  return (
    <div 
      ref={scrollContainerRef}
      className="h-full overflow-auto scroll-smooth"
    >
      <div className="p-6 space-y-6 relative">
        {/* Preview or Code */}
        {viewMode === 'preview' ? (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Live Preview</h3>
            <ComponentDemoDisplay component={component} variant={variant} />
          </div>
        ) : (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Usage Example</h3>
            <CodeBlock code={variant.code} />
          </div>
        )}

        {/* Props Info */}
        {Object.keys(variant.props).length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-medium">Props</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPropsExpanded(!propsExpanded)}
                className="h-8 px-2 gap-1"
              >
                {propsExpanded ? (
                  <ChevronDown className="h-3 w-3" />
                ) : (
                  <ChevronRight className="h-3 w-3" />
                )}
                <span className="text-xs">
                  {propsExpanded ? 'Collapse' : 'Expand'}
                </span>
              </Button>
            </div>
            
            {propsExpanded && (
              <Card>
                <CardContent className="p-4">
                  <div className="max-h-64 overflow-auto scroll-smooth border rounded bg-muted/30">
                    <pre className="p-3 text-sm text-muted-foreground">
                      {JSON.stringify(variant.props, null, 2)}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Extra spacing at bottom for better scroll experience */}
        <div className="h-8" />
      </div>
    </div>
  )
}