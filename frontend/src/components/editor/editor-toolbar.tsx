"use client";

import React from 'react';
import { Editor } from '@tiptap/react';
import { 
  Bold, 
  Italic, 
  Code, 
  Strikethrough,
  List,
  ListOrdered,
  Quote,
  Heading1,
  Heading2,
  Heading3,
  Undo,
  Redo,
  Type
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ToolbarOptions } from '@/lib/editor/editor-types';
import { cn } from '@/lib/utils';

interface EditorToolbarProps {
  editor: Editor | null;
  options?: ToolbarOptions;
  className?: string;
}

export function EditorToolbar({ 
  editor, 
  options = {}, 
  className 
}: EditorToolbarProps) {
  if (!editor) {
    return null;
  }

  const {
    showBold = true,
    showItalic = true,
    showCode = true,
    showStrike = true,
    showHeadings = true,
    showLists = true,
    showCodeBlock = true,
    showBlockquote = true,
    showUndo = true,
    showRedo = true,
  } = options;

  return (
    <div className={cn(
      "flex items-center gap-1 p-2 border-b bg-background",
      className
    )}>
      {/* Undo/Redo */}
      {(showUndo || showRedo) && (
        <>
          {showUndo && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().undo().run()}
              disabled={!editor.can().undo()}
              className="h-8 w-8 p-0"
            >
              <Undo className="h-4 w-4" />
            </Button>
          )}
          {showRedo && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().redo().run()}
              disabled={!editor.can().redo()}
              className="h-8 w-8 p-0"
            >
              <Redo className="h-4 w-4" />
            </Button>
          )}
          <Separator orientation="vertical" className="h-6" />
        </>
      )}

      {/* Text Formatting */}
      {(showBold || showItalic || showCode || showStrike) && (
        <>
          {showBold && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={cn(
                "h-8 w-8 p-0",
                editor.isActive('bold') && "bg-secondary"
              )}
            >
              <Bold className="h-4 w-4" />
            </Button>
          )}
          {showItalic && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={cn(
                "h-8 w-8 p-0",
                editor.isActive('italic') && "bg-secondary"
              )}
            >
              <Italic className="h-4 w-4" />
            </Button>
          )}
          {showCode && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().toggleCode().run()}
              className={cn(
                "h-8 w-8 p-0",
                editor.isActive('code') && "bg-secondary"
              )}
            >
              <Code className="h-4 w-4" />
            </Button>
          )}
          {showStrike && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().toggleStrike().run()}
              className={cn(
                "h-8 w-8 p-0",
                editor.isActive('strike') && "bg-secondary"
              )}
            >
              <Strikethrough className="h-4 w-4" />
            </Button>
          )}
          <Separator orientation="vertical" className="h-6" />
        </>
      )}

      {/* Headings */}
      {showHeadings && (
        <>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            className={cn(
              "h-8 w-8 p-0",
              editor.isActive('heading', { level: 1 }) && "bg-secondary"
            )}
          >
            <Heading1 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            className={cn(
              "h-8 w-8 p-0",
              editor.isActive('heading', { level: 2 }) && "bg-secondary"
            )}
          >
            <Heading2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            className={cn(
              "h-8 w-8 p-0",
              editor.isActive('heading', { level: 3 }) && "bg-secondary"
            )}
          >
            <Heading3 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().setParagraph().run()}
            className={cn(
              "h-8 w-8 p-0",
              editor.isActive('paragraph') && "bg-secondary"
            )}
          >
            <Type className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="h-6" />
        </>
      )}

      {/* Lists */}
      {showLists && (
        <>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={cn(
              "h-8 w-8 p-0",
              editor.isActive('bulletList') && "bg-secondary"
            )}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={cn(
              "h-8 w-8 p-0",
              editor.isActive('orderedList') && "bg-secondary"
            )}
          >
            <ListOrdered className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="h-6" />
        </>
      )}

      {/* Block Elements */}
      {(showBlockquote || showCodeBlock) && (
        <>
          {showBlockquote && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().toggleBlockquote().run()}
              className={cn(
                "h-8 w-8 p-0",
                editor.isActive('blockquote') && "bg-secondary"
              )}
            >
              <Quote className="h-4 w-4" />
            </Button>
          )}
          {showCodeBlock && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => editor.chain().focus().toggleCodeBlock().run()}
              className={cn(
                "h-8 px-2",
                editor.isActive('codeBlock') && "bg-secondary"
              )}
            >
              <Code className="h-4 w-4 mr-1" />
              <span className="text-xs">Block</span>
            </Button>
          )}
        </>
      )}
    </div>
  );
}

export default EditorToolbar;