import {
  Bold,
  Italic,
  Underline as UnderlineIcon,
  Strikethrough,
  Code,
  Highlighter,
  Subscript as SubscriptIcon,
  Superscript as SuperscriptIcon,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  List,
  ListOrdered,
  CheckSquare,
  Quote,
  Minus,
  // Image icon is used directly in toolbar
  Table as TableIcon,
  Code2,
  Heading1,
  Heading2,
  Heading3,
  Undo,
  Redo,
  Type,
  Columns,
  Rows,
  Merge,
  Split,
  ChevronDown,
  MoreHorizontal,
} from "lucide-react";
import type { EditorCommand } from "../types/editor.types";

// Default editor content and configuration
export const EDITOR_DEFAULTS = {
  content: "<p>Hello World! 🌎️</p>",
  placeholder: "Start writing...",
  minHeight: 300,
  characterLimit: null,
} as const;

// File upload configuration
export const IMAGE_UPLOAD_CONFIG = {
  allowedMimeTypes: [
    "image/png",
    "image/jpeg", 
    "image/gif",
    "image/webp",
  ],
  maxFileSize: 10 * 1024 * 1024, // 10MB
  acceptString: "image/*",
};

// Editor extension configurations
export const EXTENSION_CONFIGS = {
  starterKit: {
    heading: {
      levels: [1, 2, 3] as [1, 2, 3],
    },
    codeBlock: {
      HTMLAttributes: {
        class: "bg-gray-100 dark:bg-gray-800 rounded-md p-3 font-mono text-sm",
      },
    },
  },
  textAlign: {
    types: ["heading", "paragraph"],
  },
  highlight: {
    multicolor: true,
  },
  link: {
    openOnClick: false,
    HTMLAttributes: {
      class: "text-blue-600 underline cursor-pointer",
    },
  },
  image: {
    HTMLAttributes: {
      class: "max-w-full h-auto rounded-lg",
    },
  },
  taskItem: {
    nested: true,
  },
  table: {
    resizable: true,
  },
};

// Editor props configuration
export const EDITOR_PROPS = {
  attributes: {
    class: "tiptap prose prose-sm focus:outline-none max-w-none",
  },
} as const;

// Toolbar button configurations
export const TOOLBAR_BUTTONS = {
  // History buttons
  history: [
    {
      id: "undo",
      icon: Undo,
      tooltip: "Undo",
      shortcutKeys: "Ctrl+Z",
      command: "undo" as EditorCommand,
    },
    {
      id: "redo", 
      icon: Redo,
      tooltip: "Redo",
      shortcutKeys: "Ctrl+Y",
      command: "redo" as EditorCommand,
    },
  ],
  
  // Basic formatting buttons
  formatting: [
    {
      id: "bold",
      icon: Bold,
      tooltip: "Bold",
      shortcutKeys: "Ctrl+B",
      command: "toggleBold" as EditorCommand,
      stateKey: "isBold",
    },
    {
      id: "italic",
      icon: Italic,
      tooltip: "Italic", 
      shortcutKeys: "Ctrl+I",
      command: "toggleItalic" as EditorCommand,
      stateKey: "isItalic",
    },
    {
      id: "highlight",
      icon: Highlighter,
      tooltip: "Highlight",
      command: "toggleHighlight" as EditorCommand,
      stateKey: "isHighlight",
      shortcutKeys: undefined,
    },
  ],

  // List buttons
  lists: [
    {
      id: "bulletList",
      icon: List,
      tooltip: "Bullet List",
      command: "toggleBulletList" as EditorCommand,
      stateKey: "isBulletList",
      shortcutKeys: undefined,
    },
    {
      id: "orderedList",
      icon: ListOrdered,
      tooltip: "Numbered List", 
      command: "toggleOrderedList" as EditorCommand,
      stateKey: "isOrderedList",
      shortcutKeys: undefined,
    },
    {
      id: "taskList",
      icon: CheckSquare,
      tooltip: "Task List",
      command: "toggleTaskList" as EditorCommand, 
      stateKey: "isTaskList",
      shortcutKeys: undefined,
    },
  ],

  // Block buttons
  blocks: [
    {
      id: "blockquote",
      icon: Quote,
      tooltip: "Blockquote",
      command: "toggleBlockquote" as EditorCommand,
      stateKey: "isBlockquote",
      shortcutKeys: undefined,
    },
  ],

  // Insert buttons
  insert: [
    {
      id: "horizontalRule", 
      icon: Minus,
      tooltip: "Horizontal Rule",
      command: "setHorizontalRule" as EditorCommand,
      shortcutKeys: undefined,
    },
  ],
} as const;

// Text style options
export const TEXT_STYLE_OPTIONS = [
  {
    id: "paragraph",
    label: "Normal Text",
    icon: Type,
    command: "setParagraph" as EditorCommand,
    level: null,
  },
  {
    id: "heading1",
    label: "Heading 1", 
    icon: Heading1,
    command: "toggleHeading" as EditorCommand,
    level: 1,
  },
  {
    id: "heading2",
    label: "Heading 2",
    icon: Heading2,
    command: "toggleHeading" as EditorCommand, 
    level: 2,
  },
  {
    id: "heading3",
    label: "Heading 3",
    icon: Heading3,
    command: "toggleHeading" as EditorCommand,
    level: 3,
  },
] as const;

// Text alignment options
export const TEXT_ALIGNMENT_OPTIONS = [
  {
    id: "left",
    label: "Align Left",
    icon: AlignLeft,
    command: "setTextAlign" as EditorCommand,
    value: "left",
  },
  {
    id: "center",
    label: "Center",
    icon: AlignCenter,
    command: "setTextAlign" as EditorCommand,
    value: "center",
  },
  {
    id: "right", 
    label: "Align Right",
    icon: AlignRight,
    command: "setTextAlign" as EditorCommand,
    value: "right",
  },
  {
    id: "justify",
    label: "Justify",
    icon: AlignJustify,
    command: "setTextAlign" as EditorCommand,
    value: "justify",
  },
] as const;

// Special formatting options
export const SPECIAL_FORMATTING_OPTIONS = [
  {
    id: "underline",
    label: "Underline",
    icon: UnderlineIcon,
    command: "toggleUnderline" as EditorCommand,
    stateKey: "isUnderline",
  },
  {
    id: "strikethrough",
    label: "Strikethrough",
    icon: Strikethrough,
    command: "toggleStrike" as EditorCommand,
    stateKey: "isStrike",
  },
  {
    id: "code",
    label: "Inline Code",
    icon: Code,
    command: "toggleCode" as EditorCommand,
    stateKey: "isCode",
  },
  {
    id: "codeBlock",
    label: "Code Block",
    icon: Code2,
    command: "toggleCodeBlock" as EditorCommand,
    stateKey: "isCodeBlock",
  },
  {
    id: "subscript",
    label: "Subscript",
    icon: SubscriptIcon,
    command: "toggleSubscript" as EditorCommand,
    stateKey: "isSubscript",
  },
  {
    id: "superscript",
    label: "Superscript", 
    icon: SuperscriptIcon,
    command: "toggleSuperscript" as EditorCommand,
    stateKey: "isSuperscript",
  },
] as const;

// Table options
export const TABLE_OPTIONS = [
  {
    id: "insertTable",
    label: "Insert Table (3×3)",
    icon: TableIcon,
    command: "insertTable" as EditorCommand,
    params: { rows: 3, cols: 3, withHeaderRow: true },
  },
  {
    id: "addColumnBefore",
    label: "Add Column Before",
    icon: Columns,
    command: "addColumnBefore" as EditorCommand,
  },
  {
    id: "addColumnAfter",
    label: "Add Column After", 
    icon: Columns,
    command: "addColumnAfter" as EditorCommand,
  },
  {
    id: "addRowBefore",
    label: "Add Row Before",
    icon: Rows,
    command: "addRowBefore" as EditorCommand,
  },
  {
    id: "addRowAfter",
    label: "Add Row After",
    icon: Rows,
    command: "addRowAfter" as EditorCommand,
  },
  {
    id: "mergeCells",
    label: "Merge Cells",
    icon: Merge,
    command: "mergeCells" as EditorCommand,
  },
  {
    id: "splitCell",
    label: "Split Cell",
    icon: Split,
    command: "splitCell" as EditorCommand,
  },
  {
    id: "deleteColumn",
    label: "Delete Column",
    icon: Columns,
    command: "deleteColumn" as EditorCommand,
    variant: "destructive",
  },
  {
    id: "deleteRow",
    label: "Delete Row",
    icon: Rows,
    command: "deleteRow" as EditorCommand,
    variant: "destructive",
  },
  {
    id: "deleteTable",
    label: "Delete Table",
    icon: TableIcon,
    command: "deleteTable" as EditorCommand,
    variant: "destructive",
  },
] as const;

// UI icons
export const UI_ICONS = {
  chevronDown: ChevronDown,
  moreHorizontal: MoreHorizontal,
} as const;