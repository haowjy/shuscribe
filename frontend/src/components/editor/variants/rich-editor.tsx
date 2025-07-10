"use client";

import React from 'react';
import { TiptapEditor } from '../tiptap-editor';
import { BaseEditorProps } from '@/lib/editor/editor-types';

// Rich editor with all formatting options
const RICH_TOOLBAR_OPTIONS = {
  showBold: true,
  showItalic: true,
  showCode: true,
  showStrike: true,
  showHeadings: true,
  showLists: true,
  showCodeBlock: true,
  showBlockquote: true,
  showUndo: true,
  showRedo: true,
};

interface RichEditorProps extends Omit<BaseEditorProps, 'variant'> {
  // Additional props specific to rich editor
  enableCodeBlocks?: boolean;
  enableTables?: boolean;
}

export function RichEditor({
  enableCodeBlocks = true,
  enableTables = false,
  ...props
}: RichEditorProps) {
  const toolbarOptions = {
    ...RICH_TOOLBAR_OPTIONS,
    showCodeBlock: enableCodeBlocks,
  };

  // TODO: Add table extension when enableTables is true
  const extensions = [...(props.extensions || [])];

  return (
    <TiptapEditor
      {...props}
      variant="rich"
      extensions={extensions}
      toolbarOptions={toolbarOptions}
      placeholder={props.placeholder || "Start writing with rich formatting..."}
    />
  );
}

export default RichEditor;