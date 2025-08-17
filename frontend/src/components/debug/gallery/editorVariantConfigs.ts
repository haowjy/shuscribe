import { FileText, MessageSquare, StickyNote } from 'lucide-react'
import { ToolbarConfig, FooterConfig } from '@/components/editor/types/editor.types'

export interface EditorVariantConfig {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  placeholder: string
  toolbar?: ToolbarConfig
  footer?: FooterConfig
  editable?: boolean
  infoPanels: InfoPanel[]
}

export interface InfoPanel {
  title: string
  type: 'features' | 'useCases' | 'configuration' | 'shortcuts'
  content: InfoPanelContent
}

export interface InfoPanelContent {
  items?: Array<{ icon?: string; label: string; description: string }>
  list?: string[]
  code?: string
  shortcuts?: Array<{ key: string; description: string }>
}

export const editorVariantConfigs: EditorVariantConfig[] = [
  {
    id: 'full',
    title: 'Full Editor',
    description: 'Full-featured editor with all toolbar sections',
    icon: FileText,
    placeholder: 'Start typing to test all editor features...',
    // Uses default config - all features enabled
    infoPanels: [
      {
        title: 'Customization Features',
        type: 'features',
        content: {
          items: [
            { icon: '✅', label: 'Toolbar Sections', description: 'Choose which sections to include (history, textStyle, formatting, lists, alignment, blocks, insert, table)' },
            { icon: '✅', label: 'Individual Commands', description: 'Select specific commands to show (toggleBold, toggleItalic, etc.)' },
            { icon: '✅', label: 'Footer Config', description: 'Toggle character count, word count, stats' },
            { icon: '✅', label: 'Extension Overrides', description: 'Customize highlight, link, table behaviors' },
            { icon: '✅', label: 'Composition Pattern', description: 'Use hooks and primitives for custom editors' }
          ]
        }
      },
      {
        title: 'Editor Variants',
        type: 'useCases',
        content: {
          items: [
            { icon: '📝', label: 'Full Editor', description: 'All features enabled' },
            { icon: '💬', label: 'Chat Editor', description: 'Basic formatting only' },
            { icon: '📄', label: 'Notes Editor', description: 'Minimal toolbar' },
            { icon: '🎯', label: 'Custom', description: 'Use hooks for complete control' }
          ]
        }
      },
      {
        title: 'Quick Tips',
        type: 'shortcuts',
        content: {
          list: [
            'Use toolbar buttons for all formatting',
            'Active formatting shows highlighted buttons',
            'Try task lists with checkboxes',
            'Insert tables with resizable columns',
            'Text alignment works on headings too',
            'Link/image prompts for URLs',
            'Character count updates live',
            'All keyboard shortcuts still work!'
          ]
        }
      }
    ]
  },
  {
    id: 'chat',
    title: 'Chat Editor',
    description: 'Lightweight editor for messaging interfaces',
    icon: MessageSquare,
    placeholder: 'Type a message...',
    editable: false,
    toolbar: {
      show: false
    },
    footer: {
      show: false
    },
    infoPanels: [
      {
        title: 'Chat Features',
        type: 'features',
        content: {
          items: [
            { icon: '💬', label: 'Quick Formatting', description: 'Bold, italic, and highlighting' },
            { icon: '📋', label: 'Lists', description: 'Bullet and numbered lists' },
            { icon: '↔️', label: 'Alignment', description: 'Left, center, right alignment' },
            { icon: '⏮️', label: 'History', description: 'Undo and redo support' },
            { icon: '🎯', label: 'Focused', description: 'No footer clutter for clean UI' }
          ]
        }
      },
      {
        title: 'Use Cases',
        type: 'useCases',
        content: {
          list: [
            'Messaging applications',
            'Comment systems',
            'Quick reply interfaces',
            'Live chat widgets',
            'Social media posts',
            'Forum responses'
          ]
        }
      },
      {
        title: 'Configuration',
        type: 'configuration',
        content: {
          code: `toolbar={{
  sections: [
    "history", 
    "formatting", 
    "lists", 
    "alignment"
  ],
  commands: [
    "undo", "redo",
    "toggleBold", "toggleItalic",
    "toggleHighlight",
    "toggleBulletList",
    "toggleOrderedList",
    "setTextAlign"
  ]
}}
footer={{ show: false }}`
        }
      }
    ]
  },
  {
    id: 'notes',
    title: 'Notes Editor',
    description: 'Minimal editor for quick note-taking',
    icon: StickyNote,
    placeholder: 'Add a quick note...',
    toolbar: {
      sections: ['formatting' as const],
      commands: ['toggleBold' as const, 'toggleItalic' as const]
    },
    footer: {
      showCharacterCount: false,
      showWordCount: false
    },
    infoPanels: [
      {
        title: 'Minimal Features',
        type: 'features',
        content: {
          items: [
            { icon: '✏️', label: 'Basic Formatting', description: 'Bold and italic only' },
            { icon: '🚫', label: 'No Footer', description: 'Clean interface without counts' },
            { icon: '⚡', label: 'Lightweight', description: 'Fastest loading variant' },
            { icon: '🎯', label: 'Focused', description: 'Distraction-free writing' },
            { icon: '📱', label: 'Mobile-First', description: 'Perfect for small screens' }
          ]
        }
      },
      {
        title: 'Perfect For',
        type: 'useCases',
        content: {
          list: [
            'Quick jotting down ideas',
            'Simple text input forms',
            'Mobile note-taking apps',
            'Minimal content editing',
            'Todo list descriptions',
            'Caption and label editing'
          ]
        }
      },
      {
        title: 'Configuration',
        type: 'configuration',
        content: {
          code: `toolbar={{
  sections: ["formatting"],
  commands: [
    "toggleBold", 
    "toggleItalic"
  ]
}}
footer={{
  showCharacterCount: false,
  showWordCount: false
}}`
        }
      },
      {
        title: 'Keyboard Shortcuts',
        type: 'shortcuts',
        content: {
          shortcuts: [
            { key: '⌘ B', description: 'Bold' },
            { key: '⌘ I', description: 'Italic' },
            { key: '⌘ Z', description: 'Undo' },
            { key: '⌘ ⇧ Z', description: 'Redo' }
          ]
        }
      }
    ]
  }
]