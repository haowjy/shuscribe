import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { DocumentEditor } from '@/components/editor/DocumentEditor'
import { StatusBadge } from '@/components/projects/StatusBadge'
import { EditorTabs } from '@/components/editor/tabs/EditorTabs'
import { AIChat } from '@/components/chat/AIChat'
import { Explorer } from '@/components/workspace/explorer/Explorer'
import { Dialog } from '@/components/ui/dialog'
import { DropdownMenu } from '@/components/ui/dropdown-menu'
import { ResizablePanelGroup } from '@/components/ui/resizable'
import { ComponentType } from 'react'

// Base types for our gallery system
export interface ComponentVariant {
  id: string
  name: string
  description: string
  props: Record<string, unknown>
  code: string
}

export interface ComponentDefinition {
  id: string
  name: string
  description: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  component: ComponentType<any>
  category: string
  variants: ComponentVariant[]
  defaultVariantId: string
}

export interface ComponentCategory {
  id: string
  name: string
  description: string
  components: ComponentDefinition[]
}

// Button variants
const buttonVariants: ComponentVariant[] = [
  {
    id: 'default',
    name: 'Default',
    description: 'Primary action button',
    props: { children: 'Button', variant: 'default' },
    code: '<Button>Button</Button>'
  },
  {
    id: 'destructive',
    name: 'Destructive',
    description: 'For dangerous actions',
    props: { children: 'Delete', variant: 'destructive' },
    code: '<Button variant="destructive">Delete</Button>'
  },
  {
    id: 'outline',
    name: 'Outline',
    description: 'Secondary button style',
    props: { children: 'Cancel', variant: 'outline' },
    code: '<Button variant="outline">Cancel</Button>'
  },
  {
    id: 'secondary',
    name: 'Secondary',
    description: 'Subtle secondary action',
    props: { children: 'Secondary', variant: 'secondary' },
    code: '<Button variant="secondary">Secondary</Button>'
  },
  {
    id: 'ghost',
    name: 'Ghost',
    description: 'Minimal button style',
    props: { children: 'Ghost', variant: 'ghost' },
    code: '<Button variant="ghost">Ghost</Button>'
  },
  {
    id: 'link',
    name: 'Link',
    description: 'Text link style',
    props: { children: 'Link', variant: 'link' },
    code: '<Button variant="link">Link</Button>'
  },
  {
    id: 'sizes',
    name: 'Sizes',
    description: 'Different button sizes',
    props: { children: 'Small', size: 'sm' },
    code: '<Button size="sm">Small</Button>\n<Button size="default">Default</Button>\n<Button size="lg">Large</Button>'
  }
]

// Badge variants
const badgeVariants: ComponentVariant[] = [
  {
    id: 'default',
    name: 'Default',
    description: 'Primary badge style',
    props: { children: 'Badge' },
    code: '<Badge>Badge</Badge>'
  },
  {
    id: 'secondary',
    name: 'Secondary',
    description: 'Secondary badge style',
    props: { children: 'Secondary', variant: 'secondary' },
    code: '<Badge variant="secondary">Secondary</Badge>'
  },
  {
    id: 'destructive',
    name: 'Destructive',
    description: 'Error or warning badge',
    props: { children: 'Error', variant: 'destructive' },
    code: '<Badge variant="destructive">Error</Badge>'
  },
  {
    id: 'outline',
    name: 'Outline',
    description: 'Outlined badge style',
    props: { children: 'Outline', variant: 'outline' },
    code: '<Badge variant="outline">Outline</Badge>'
  }
]

// Card variants
const cardVariants: ComponentVariant[] = [
  {
    id: 'basic',
    name: 'Basic Card',
    description: 'Simple card with content',
    props: {
      hasChildren: true,
      variant: 'basic'
    },
    code: `<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>This is the main content of the card.</p>
  </CardContent>
</Card>`
  },
  {
    id: 'with-footer',
    name: 'Card with Footer',
    description: 'Card with actions in footer',
    props: {
      hasChildren: true,
      variant: 'with-footer'
    },
    code: `<Card>
  <CardHeader>
    <CardTitle>Project Overview</CardTitle>
    <CardDescription>Manage your writing project</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Track your progress, manage chapters, and collaborate with others.</p>
  </CardContent>
  <CardFooter>
    <Button variant="outline" size="sm">Cancel</Button>
    <Button size="sm">Save Changes</Button>
  </CardFooter>
</Card>`
  }
]

// Input variants
const inputVariants: ComponentVariant[] = [
  {
    id: 'basic',
    name: 'Basic Input',
    description: 'Standard text input',
    props: { placeholder: 'Enter text...' },
    code: '<Input placeholder="Enter text..." />'
  },
  {
    id: 'with-label',
    name: 'Input with Label',
    description: 'Labeled input field',
    props: {
      hasChildren: true,
      variant: 'with-label'
    },
    code: `<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" placeholder="Enter your email" />
</div>`
  }
]

// Editor variants
const editorVariants: ComponentVariant[] = [
  {
    id: 'minimal',
    name: 'Minimal Editor',
    description: 'Basic editor with minimal toolbar',
    props: {
      placeholder: 'Start writing...',
      toolbar: {
        enabled: true,
        sections: ['formatting']
      },
      footer: { enabled: false }
    },
    code: `<DocumentEditor 
  placeholder="Start writing..."
  toolbar={{
    enabled: true,
    sections: ['formatting']
  }}
  footer={{ enabled: false }}
/>`
  },
  {
    id: 'full',
    name: 'Full Editor',
    description: 'Complete editor with all features',
    props: {
      placeholder: 'Write your story...',
      toolbar: {
        enabled: true,
        sections: ['formatting', 'content', 'layout']
      },
      footer: {
        enabled: true,
        sections: ['wordCount', 'save']
      }
    },
    code: `<DocumentEditor 
  placeholder="Write your story..."
  toolbar={{
    enabled: true,
    sections: ['formatting', 'content', 'layout']
  }}
  footer={{
    enabled: true,
    sections: ['wordCount', 'save']
  }}
/>`
  },
  {
    id: 'chat-optimized',
    name: 'Chat Optimized',
    description: 'Streamlined for chat and quick responses',
    props: {
      placeholder: 'Type your message...',
      toolbar: {
        enabled: true,
        sections: ['formatting']
      },
      footer: { 
        enabled: true,
        sections: ['wordCount']
      }
    },
    code: `<DocumentEditor 
  placeholder="Type your message..."
  toolbar={{
    enabled: true,
    sections: ['formatting']
  }}
  footer={{
    enabled: true,
    sections: ['wordCount']
  }}
/>`
  },
  {
    id: 'note-taking',
    name: 'Note Taking',
    description: 'Optimized for quick notes and ideas',
    props: {
      placeholder: 'Jot down your ideas...',
      toolbar: {
        enabled: true,
        sections: ['formatting', 'content']
      },
      footer: {
        enabled: true,
        sections: ['wordCount', 'save']
      }
    },
    code: `<DocumentEditor 
  placeholder="Jot down your ideas..."
  toolbar={{
    enabled: true,
    sections: ['formatting', 'content']
  }}
  footer={{
    enabled: true,
    sections: ['wordCount', 'save']
  }}
/>`
  },
  {
    id: 'focus-mode',
    name: 'Focus Mode',
    description: 'Distraction-free writing experience',
    props: {
      placeholder: 'Enter your flow state...',
      toolbar: {
        enabled: false
      },
      footer: {
        enabled: true,
        sections: ['wordCount']
      }
    },
    code: `<DocumentEditor 
  placeholder="Enter your flow state..."
  toolbar={{
    enabled: false
  }}
  footer={{
    enabled: true,
    sections: ['wordCount']
  }}
/>`
  },
  {
    id: 'outline-mode',
    name: 'Outline Mode',
    description: 'Structured writing with outline tools',
    props: {
      placeholder: 'Create your outline...',
      toolbar: {
        enabled: true,
        sections: ['formatting', 'layout']
      },
      footer: {
        enabled: true,
        sections: ['wordCount', 'save']
      }
    },
    code: `<DocumentEditor 
  placeholder="Create your outline..."
  toolbar={{
    enabled: true,
    sections: ['formatting', 'layout']
  }}
  footer={{
    enabled: true,
    sections: ['wordCount', 'save']
  }}
/>`
  }
]

// Status Badge variants
const statusBadgeVariants: ComponentVariant[] = [
  {
    id: 'draft',
    name: 'Draft Status',
    description: 'Work in progress status',
    props: { tag: 'Draft' },
    code: '<StatusBadge tag="Draft" />'
  },
  {
    id: 'complete',
    name: 'Complete Status',
    description: 'Finished work status',
    props: { tag: 'Complete' },
    code: '<StatusBadge tag="Complete" />'
  },
  {
    id: 'review',
    name: 'In Review',
    description: 'Under review status',
    props: { tag: 'In Review' },
    code: '<StatusBadge tag="In Review" />'
  }
]

// Editor Tabs variants
const editorTabsVariants: ComponentVariant[] = [
  {
    id: 'basic',
    name: 'Basic Tabs',
    description: 'Simple tab interface with a few tabs',
    props: {
      hasChildren: true,
      variant: 'basic',
      tabs: [
        { id: '1', name: 'Chapter 1', hasUnsavedChanges: false, path: '/chapters/chapter-1' },
        { id: '2', name: 'Character Notes', hasUnsavedChanges: true, path: '/notes/characters' },
        { id: '3', name: 'World Building', hasUnsavedChanges: false, path: '/notes/world' }
      ],
      activeTabId: '1'
    },
    code: `<EditorTabs 
  tabs={[
    { id: '1', name: 'Chapter 1', hasUnsavedChanges: false },
    { id: '2', name: 'Character Notes', hasUnsavedChanges: true },
    { id: '3', name: 'World Building', hasUnsavedChanges: false }
  ]}
  activeTabId="1"
  onTabSelect={(id) => console.log('Selected:', id)}
  onTabClose={(id) => console.log('Closed:', id)}
  onNewTab={() => console.log('New tab')}
/>`
  },
  {
    id: 'overflow',
    name: 'Many Tabs',
    description: 'Overflow behavior with scrolling and gradients',
    props: {
      hasChildren: true,
      variant: 'overflow',
      tabs: [
        { id: '1', name: 'Chapter 1: The Beginning', hasUnsavedChanges: false },
        { id: '2', name: 'Chapter 2: Rising Action', hasUnsavedChanges: true },
        { id: '3', name: 'Character Development Notes', hasUnsavedChanges: false },
        { id: '4', name: 'World Building Document', hasUnsavedChanges: true },
        { id: '5', name: 'Plot Outline and Structure', hasUnsavedChanges: false },
        { id: '6', name: 'Research Notes', hasUnsavedChanges: false },
        { id: '7', name: 'Chapter 3: Climax', hasUnsavedChanges: true },
        { id: '8', name: 'Epilogue Draft', hasUnsavedChanges: false }
      ],
      activeTabId: '3'
    },
    code: `<EditorTabs 
  tabs={manyTabs}
  activeTabId="3"
  onTabSelect={handleTabSelect}
  onTabClose={handleTabClose}
  onNewTab={handleNewTab}
  onReorderTabs={handleReorderTabs}
/>`
  },
  {
    id: 'unsaved',
    name: 'Unsaved Changes',
    description: 'Tabs with unsaved change indicators',
    props: {
      hasChildren: true,
      variant: 'unsaved',
      tabs: [
        { id: '1', name: 'Draft Chapter', hasUnsavedChanges: true },
        { id: '2', name: 'Character Sheet', hasUnsavedChanges: true },
        { id: '3', name: 'Published Story', hasUnsavedChanges: false }
      ],
      activeTabId: '2'
    },
    code: `<EditorTabs 
  tabs={[
    { id: '1', name: 'Draft Chapter', hasUnsavedChanges: true },
    { id: '2', name: 'Character Sheet', hasUnsavedChanges: true },
    { id: '3', name: 'Published Story', hasUnsavedChanges: false }
  ]}
  activeTabId="2"
  onTabSelect={handleTabSelect}
  onTabClose={handleTabClose}
  onNewTab={handleNewTab}
/>`
  },
  {
    id: 'empty',
    name: 'Empty State',
    description: 'Empty tabs with new document prompt',
    props: {
      hasChildren: true,
      variant: 'empty',
      tabs: [],
      activeTabId: ''
    },
    code: `<EditorTabs 
  tabs={[]}
  activeTabId=""
  onTabSelect={handleTabSelect}
  onTabClose={handleTabClose}
  onNewTab={handleNewTab}
/>`
  }
]

// AI Chat variants
const aiChatVariants: ComponentVariant[] = [
  {
    id: 'empty',
    name: 'Empty Chat',
    description: 'Chat interface with no conversation history',
    props: {
      hasChildren: true,
      variant: 'empty',
      thread: null
    },
    code: `<AIChat 
  thread={null}
  onUpdateMessages={(messages) => console.log('Messages updated:', messages)}
  onNewThread={() => console.log('New thread requested')}
/>`
  },
  {
    id: 'conversation',
    name: 'Active Conversation',
    description: 'Chat with user and assistant messages',
    props: {
      hasChildren: true,
      variant: 'conversation',
      thread: {
        id: 'thread-1',
        title: 'Story Development Discussion',
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Help me develop a fantasy character who is a reluctant hero.'
          },
          {
            id: 'msg-2',
            role: 'assistant',
            content: 'I\'d be happy to help you develop a reluctant hero! Let\'s start with their background. What circumstances force them into heroism despite their reluctance? Are they avoiding responsibility due to fear, past trauma, or perhaps they simply prefer a quiet life?'
          },
          {
            id: 'msg-3',
            role: 'user',
            content: 'They\'re a former knight who lost their squad in battle and now works as a blacksmith in a small village.'
          }
        ]
      }
    },
    code: `<AIChat 
  thread={threadWithMessages}
  onUpdateMessages={handleUpdateMessages}
  onNewThread={handleNewThread}
/>`
  },
  {
    id: 'long-conversation',
    name: 'Long Conversation',
    description: 'Extended chat demonstrating scrolling behavior',
    props: {
      hasChildren: true,
      variant: 'long-conversation',
      thread: {
        id: 'thread-2',
        title: 'World Building Session',
        messages: [
          {
            id: 'msg-1',
            role: 'user',
            content: 'I need help creating a magic system for my fantasy novel.'
          },
          {
            id: 'msg-2',
            role: 'assistant',
            content: 'Excellent! Let\'s build a compelling magic system. First, what\'s the source of magic in your world? Is it innate to certain people, drawn from the environment, or perhaps tied to emotions or knowledge?'
          },
          {
            id: 'msg-3',
            role: 'user',
            content: 'I like the idea of magic being tied to emotions, but with consequences for using it.'
          },
          {
            id: 'msg-4',
            role: 'assistant',
            content: 'Emotion-based magic with consequences is fascinating! This creates natural character development opportunities. What kind of consequences are you thinking? Physical exhaustion? Emotional numbness? Or perhaps the magic amplifies the emotion used, making it harder to control?'
          },
          {
            id: 'msg-5',
            role: 'user',
            content: 'Maybe using magic drains the corresponding emotion temporarily? So if you use anger-based fire magic, you become eerily calm afterwards.'
          },
          {
            id: 'msg-6',
            role: 'assistant',
            content: 'That\'s brilliant! This creates a compelling trade-off where powerful magic comes at the cost of emotional balance. Characters would need to carefully consider when to use magic, and it opens up interesting plot possibilities. How long does this emotional drain last?'
          }
        ]
      }
    },
    code: `<AIChat 
  thread={longThread}
  onUpdateMessages={handleUpdateMessages}
  onNewThread={handleNewThread}
/>`
  },
  {
    id: 'new-thread',
    name: 'New Thread State',
    description: 'Fresh conversation start with welcoming message',
    props: {
      hasChildren: true,
      variant: 'new-thread',
      thread: {
        id: 'thread-new',
        title: 'New Conversation',
        messages: [
          {
            id: 'welcome-msg',
            role: 'assistant',
            content: 'Hello! I\'m here to help you with your creative writing projects. Whether you need help with character development, plot structure, world building, or overcoming writer\'s block, I\'m ready to assist. What would you like to work on today?'
          }
        ]
      }
    },
    code: `<AIChat 
  thread={newThread}
  onUpdateMessages={handleUpdateMessages}
  onNewThread={handleNewThread}
/>`
  }
]

// File Explorer variants
const fileExplorerVariants: ComponentVariant[] = [
  {
    id: 'default',
    name: 'File Explorer',
    description: 'Complete file tree with search and navigation',
    props: {
      hasChildren: true,
      variant: 'default'
    },
    code: `<Explorer />`
  },
  {
    id: 'with-search',
    name: 'Explorer with Search',
    description: 'File tree demonstrating search filtering',
    props: {
      hasChildren: true,
      variant: 'with-search'
    },
    code: `<Explorer />
// Search functionality is built-in
// Type in the search box to filter files`
  },
  {
    id: 'empty-state',
    name: 'Empty Project',
    description: 'Explorer showing empty project state',
    props: {
      hasChildren: true,
      variant: 'empty-state'
    },
    code: `<Explorer />
// Shows empty state when no files exist
// Demonstrates new file creation prompt`
  }
]

// Dialog variants
const dialogVariants: ComponentVariant[] = [
  {
    id: 'basic',
    name: 'Basic Dialog',
    description: 'Simple modal dialog with title and content',
    props: {
      hasChildren: true,
      variant: 'basic'
    },
    code: `<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        This is a basic dialog description explaining what this modal is for.
      </DialogDescription>
    </DialogHeader>
    <div className="py-4">
      <p>Dialog content goes here.</p>
    </div>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button>Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>`
  },
  {
    id: 'form-dialog',
    name: 'Form Dialog',
    description: 'Dialog containing a form with inputs',
    props: {
      hasChildren: true,
      variant: 'form-dialog'
    },
    code: `<Dialog>
  <DialogTrigger asChild>
    <Button>Create Project</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Create New Project</DialogTitle>
      <DialogDescription>
        Enter the details for your new writing project.
      </DialogDescription>
    </DialogHeader>
    <div className="space-y-4 py-4">
      <div className="space-y-2">
        <Label htmlFor="name">Project Name</Label>
        <Input id="name" placeholder="My Amazing Story" />
      </div>
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Input id="description" placeholder="A brief description..." />
      </div>
    </div>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button>Create Project</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>`
  },
  {
    id: 'confirmation',
    name: 'Confirmation Dialog',
    description: 'Destructive action confirmation',
    props: {
      hasChildren: true,
      variant: 'confirmation'
    },
    code: `<Dialog>
  <DialogTrigger asChild>
    <Button variant="destructive">Delete Project</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Delete Project</DialogTitle>
      <DialogDescription>
        This action cannot be undone. This will permanently delete your project and all associated files.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button variant="destructive">Delete Project</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>`
  }
]

// Dropdown Menu variants
const dropdownMenuVariants: ComponentVariant[] = [
  {
    id: 'basic',
    name: 'Basic Menu',
    description: 'Simple dropdown menu with actions',
    props: {
      hasChildren: true,
      variant: 'basic'
    },
    code: `<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Options</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Edit</DropdownMenuItem>
    <DropdownMenuItem>Duplicate</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Delete</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>`
  },
  {
    id: 'with-icons',
    name: 'Menu with Icons',
    description: 'Dropdown menu with icons and shortcuts',
    props: {
      hasChildren: true,
      variant: 'with-icons'
    },
    code: `<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">
      <MoreHorizontal className="h-4 w-4" />
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>
      <Edit className="mr-2 h-4 w-4" />
      Edit <span className="ml-auto text-xs">⌘E</span>
    </DropdownMenuItem>
    <DropdownMenuItem>
      <Copy className="mr-2 h-4 w-4" />
      Duplicate <span className="ml-auto text-xs">⌘D</span>
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="text-destructive">
      <Trash className="mr-2 h-4 w-4" />
      Delete <span className="ml-auto text-xs">⌘⌫</span>
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>`
  }
]

// Resizable Panel variants
const resizablePanelVariants: ComponentVariant[] = [
  {
    id: 'horizontal',
    name: 'Horizontal Split',
    description: 'Side-by-side resizable panels',
    props: {
      hasChildren: true,
      variant: 'horizontal'
    },
    code: `<ResizablePanelGroup direction="horizontal" className="h-[200px]">
  <ResizablePanel defaultSize={40}>
    <div className="p-4 bg-muted/30">
      Left Panel
    </div>
  </ResizablePanel>
  <ResizableHandle />
  <ResizablePanel defaultSize={60}>
    <div className="p-4">
      Right Panel
    </div>
  </ResizablePanel>
</ResizablePanelGroup>`
  },
  {
    id: 'vertical',
    name: 'Vertical Split',
    description: 'Top and bottom resizable panels',
    props: {
      hasChildren: true,
      variant: 'vertical'
    },
    code: `<ResizablePanelGroup direction="vertical" className="h-[300px]">
  <ResizablePanel defaultSize={50}>
    <div className="p-4 bg-muted/30">
      Top Panel
    </div>
  </ResizablePanel>
  <ResizableHandle />
  <ResizablePanel defaultSize={50}>
    <div className="p-4">
      Bottom Panel
    </div>
  </ResizablePanel>
</ResizablePanelGroup>`
  },
  {
    id: 'three-panel',
    name: 'Three Panel Layout',
    description: 'Complex three-panel layout',
    props: {
      hasChildren: true,
      variant: 'three-panel'
    },
    code: `<ResizablePanelGroup direction="horizontal" className="h-[250px]">
  <ResizablePanel defaultSize={25} minSize={20}>
    <div className="p-4 bg-muted/30">Sidebar</div>
  </ResizablePanel>
  <ResizableHandle />
  <ResizablePanel defaultSize={50}>
    <ResizablePanelGroup direction="vertical">
      <ResizablePanel defaultSize={70}>
        <div className="p-4">Main Content</div>
      </ResizablePanel>
      <ResizableHandle />
      <ResizablePanel defaultSize={30}>
        <div className="p-4 bg-muted/20">Bottom Panel</div>
      </ResizablePanel>
    </ResizablePanelGroup>
  </ResizablePanel>
  <ResizableHandle />
  <ResizablePanel defaultSize={25} minSize={20}>
    <div className="p-4 bg-muted/30">Right Panel</div>
  </ResizablePanel>
</ResizablePanelGroup>`
  }
]

// Define component definitions
const componentDefinitions: ComponentDefinition[] = [
  {
    id: 'button',
    name: 'Button',
    description: 'Clickable button component with multiple variants',
    component: Button,
    category: 'ui',
    variants: buttonVariants,
    defaultVariantId: 'default'
  },
  {
    id: 'badge',
    name: 'Badge',
    description: 'Small status and label component',
    component: Badge,
    category: 'ui',
    variants: badgeVariants,
    defaultVariantId: 'default'
  },
  {
    id: 'card',
    name: 'Card',
    description: 'Container component for grouping related content',
    component: Card,
    category: 'ui',
    variants: cardVariants,
    defaultVariantId: 'basic'
  },
  {
    id: 'input',
    name: 'Input',
    description: 'Text input field for forms',
    component: Input,
    category: 'ui',
    variants: inputVariants,
    defaultVariantId: 'basic'
  },
  {
    id: 'document-editor',
    name: 'Document Editor',
    description: 'Rich text editor for content creation',
    component: DocumentEditor,
    category: 'editor',
    variants: editorVariants,
    defaultVariantId: 'minimal'
  },
  {
    id: 'status-badge',
    name: 'Status Badge',
    description: 'Project and content status indicator',
    component: StatusBadge,
    category: 'complex',
    variants: statusBadgeVariants,
    defaultVariantId: 'draft'
  },
  {
    id: 'editor-tabs',
    name: 'Editor Tabs',
    description: 'Tabbed document interface with drag & drop and overflow handling',
    component: EditorTabs,
    category: 'navigation',
    variants: editorTabsVariants,
    defaultVariantId: 'basic'
  },
  {
    id: 'ai-chat',
    name: 'AI Chat',
    description: 'Interactive chat interface for AI assistance and conversations',
    component: AIChat,
    category: 'chat',
    variants: aiChatVariants,
    defaultVariantId: 'empty'
  },
  {
    id: 'file-explorer',
    name: 'File Explorer',
    description: 'File tree navigation with search and folder management',
    component: Explorer,
    category: 'navigation',
    variants: fileExplorerVariants,
    defaultVariantId: 'default'
  },
  {
    id: 'dialog',
    name: 'Dialog',
    description: 'Modal dialogs for forms, confirmations, and content',
    component: Dialog,
    category: 'ui',
    variants: dialogVariants,
    defaultVariantId: 'basic'
  },
  {
    id: 'dropdown-menu',
    name: 'Dropdown Menu',
    description: 'Context menus and action dropdowns',
    component: DropdownMenu,
    category: 'ui',
    variants: dropdownMenuVariants,
    defaultVariantId: 'basic'
  },
  {
    id: 'resizable-panel',
    name: 'Resizable Panel',
    description: 'Flexible layout panels with drag-to-resize functionality',
    component: ResizablePanelGroup,
    category: 'layout',
    variants: resizablePanelVariants,
    defaultVariantId: 'horizontal'
  }
]

// Define categories
export const componentCategories: ComponentCategory[] = [
  {
    id: 'ui',
    name: 'UI Components',
    description: 'Basic user interface building blocks',
    components: componentDefinitions.filter(c => c.category === 'ui')
  },
  {
    id: 'navigation',
    name: 'Navigation',
    description: 'Tab systems, breadcrumbs, and navigation patterns',
    components: componentDefinitions.filter(c => c.category === 'navigation')
  },
  {
    id: 'chat',
    name: 'Chat & Communication',
    description: 'Chat interfaces, messaging, and conversation patterns',
    components: componentDefinitions.filter(c => c.category === 'chat')
  },
  {
    id: 'layout',
    name: 'Layout & Panels',
    description: 'Resizable panels, splits, and layout management',
    components: componentDefinitions.filter(c => c.category === 'layout')
  },
  {
    id: 'editor',
    name: 'Editor Components',
    description: 'Rich text editing and content creation',
    components: componentDefinitions.filter(c => c.category === 'editor')
  },
  {
    id: 'complex',
    name: 'Complex Components',
    description: 'Higher-level composed components',
    components: componentDefinitions.filter(c => c.category === 'complex')
  }
]

// Helper functions
export function getComponentById(id: string): ComponentDefinition | undefined {
  return componentDefinitions.find(comp => comp.id === id)
}

export function getVariantById(componentId: string, variantId: string): ComponentVariant | undefined {
  const component = getComponentById(componentId)
  return component?.variants.find(variant => variant.id === variantId)
}

export function getAllComponents(): ComponentDefinition[] {
  return componentDefinitions
}