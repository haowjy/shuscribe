# DocumentEditor Component Documentation

## Overview

The `DocumentEditor` is ShuScribe's primary rich text editing component, built on Tiptap/ProseMirror. It provides a highly configurable interface designed for maximum reusability across different content creation scenarios.

**Component Location**: `frontend/src/components/editor/DocumentEditor.tsx`

## Design Philosophy

The DocumentEditor follows a **configuration-over-implementation** approach:

- **Modular Toolbar**: Choose which toolbar sections and commands to include
- **Flexible Footer**: Show/hide different statistical displays  
- **Extension Overrides**: Configure Tiptap extensions without rebuilding
- **Styling Customization**: Control borders, containers, and layout classes
- **Context Awareness**: Adapts behavior based on rail mode (explorer, gallery, etc.)

## Core Architecture

### Component Structure
```
DocumentEditor/
├── DocumentEditor.tsx          # Main component
├── toolbar/                    # Toolbar system
│   ├── EditorToolbar.tsx      # Main toolbar container
│   ├── primitives/            # Reusable toolbar components
│   └── dropdowns/             # Dropdown menus (text style, alignment, etc.)
├── footer/                     # Footer with statistics
├── hooks/                      # Editor configuration and state
└── types/                      # TypeScript interfaces
```

### Configuration System

**Props Interface**: See `DocumentEditorProps` in `frontend/src/components/editor/types/editor.types.ts`

Key configuration areas:
- **Toolbar Config**: Control sections (history, formatting, lists, etc.) and specific commands
- **Footer Config**: Toggle character count, word count, and extended statistics
- **Extension Config**: Override Tiptap extension settings (highlight colors, link behavior, table resizing)
- **Styling Props**: Border, rounded corners, container classes, content wrapper

## Usage Patterns

### Four Main Variants

The editor is designed to support four primary use cases, demonstrated at `/component-gallery/editor/`:

1. **Full-Featured Editor** (`/component-gallery/editor/full/`)
   - All toolbar sections enabled
   - Complete footer statistics
   - Maximum functionality for document editing

2. **Chat Interface** (`/component-gallery/editor/chat/`) 
   - Streamlined toolbar (history, basic formatting, lists, alignment)
   - Hidden footer for clean messaging UI
   - Optimized for quick communication

3. **Minimal Notes** (`/component-gallery/editor/notes/`)
   - Essential formatting only (bold, italic)
   - Minimal footer
   - Distraction-free for quick notes

4. **Paper Mode** (`/component-gallery/editor/paper/`)
   - Document-like appearance with realistic page dimensions
   - Paper shadows and margins for focused writing
   - Multiple page sizes (A4, Letter, Legal)
   - Print-ready styling

### Customization Approaches

**Option 1: Configuration Props**
Use the `toolbar`, `footer`, and `extensions` props to customize the existing component.

**Option 2: Hook Composition** 
For maximum control, use the underlying hooks directly:
- `useEditorConfig()` - Core editor setup and extensions
- `useEditorToolbarState()` - Toolbar dropdown state management

**Hooks Location**: `frontend/src/components/editor/hooks/`

### Paper Mode

The editor includes a special "paper mode" that transforms the editing experience to feel like working with physical documents.

**Enabling Paper Mode**:
```tsx
// Basic paper mode (defaults to A4)
<DocumentEditor paperMode={true} />

// With automatic pagination
<DocumentEditor paperMode="A4" autoPagination={true} />

// Specific page sizes
<DocumentEditor paperMode="A4" />      // 21 × 29.7 cm
<DocumentEditor paperMode="letter" />  // 8.5 × 11 in
<DocumentEditor paperMode="legal" />   // 8.5 × 14 in

// Disabled (default)
<DocumentEditor paperMode={false} />
```

**Paper Mode Features**:
- **Realistic Dimensions**: True-to-life page sizes with proper aspect ratios
- **Document Margins**: Professional 2.5cm/2cm margins that feel natural
- **Paper Appearance**: Subtle shadows and white background creating depth
- **Automatic Pagination**: Content automatically flows to new pages with visual gaps (when enabled)
- **Print Optimization**: Styles optimized for both screen and print media
- **Responsive Design**: Adapts gracefully to mobile and tablet screens
- **Page Break Support**: Visual indicators for page boundaries on long content

**Use Cases**:
- Academic papers and research documents
- Business reports and formal communications
- Creative writing and manuscript editing
- Technical documentation
- Print-ready content creation
- Professional document preparation

**Demo**: See live example at `/component-gallery/editor/paper/`

## Technical Features

### Toolbar System
- **Sections**: history, textStyle, formatting, lists, alignment, blocks, insert, table
- **Dynamic Commands**: Buttons enable/disable based on cursor context
- **Dropdown Menus**: Text styles, alignment options, special formatting, table operations
- **Keyboard Shortcuts**: Full keyboard navigation support

### Content Support
- **Rich Text**: Bold, italic, underline, strikethrough, code, highlight
- **Typography**: Sub/superscript, multiple heading levels, configurable line height
- **Media**: Image paste/drop with DataURL conversion
- **Structure**: Lists (bullet, numbered, task), tables, blockquotes, horizontal rules
- **Code**: Inline code and code blocks with syntax highlighting

### Extension Configuration
All Tiptap extensions can be overridden via the `extensions.overrides` prop:
- **StarterKit**: Heading levels, code block styling
- **Highlight**: Single vs multi-color highlighting  
- **Link**: Click behavior, styling classes
- **Table**: Resizable columns, cell selection
- **TaskItem**: Nested task list support

### Performance & Accessibility
- **Optimized Rendering**: Fast typing response, efficient large document handling
- **Screen Reader Support**: Proper ARIA labels and keyboard navigation
- **Focus Management**: Smart focus handling for toolbar interactions
- **Mobile Ready**: Touch-friendly interface with responsive design

## Integration Patterns

### EditorPanel Integration
The DocumentEditor integrates with ShuScribe's workspace via `EditorPanel.tsx`, which provides:
- Tab management for multiple documents
- Sidebar integration (explorer, AI chat)
- Content area container with header/footer slots
- Rail mode context for toolbar behavior

### Content Management
- **State**: Content stored as ProseMirror document JSON
- **Updates**: Real-time `onUpdate` callbacks for auto-save
- **Offline**: Compatible with local storage caching
- **Sync**: Designed for eventual backend synchronization

## Future Architecture

The DocumentEditor is architected to evolve toward **block-based editing** (Notion-style):

- Current rich text editing will become the "Document" content type
- Additional content types will include "Page" (blocks), "Message" (chat), "Note" (minimal)
- Shared infrastructure (hooks, primitives, extensions) supports multiple editor types
- Migration path preserves existing rich text functionality

## Development References

**Key Files to Reference:**
- Types: `frontend/src/components/editor/types/editor.types.ts`
- Main Component: `frontend/src/components/editor/DocumentEditor.tsx`
- Configuration Hook: `frontend/src/components/editor/hooks/useEditorConfig.ts`
- Toolbar Implementation: `frontend/src/components/editor/toolbar/EditorToolbar.tsx`
- Live Examples: `frontend/src/app/component-gallery/editor/`

**Related Documentation:**
- Frontend Architecture: `frontend/CLAUDE-frontend.md`
- Overall System: `CLAUDE.md`