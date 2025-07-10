"use client";

import React from 'react';
import { TiptapEditor } from '../tiptap-editor';
import { BaseEditorProps } from '@/lib/editor/editor-types';

// Minimal editor with no formatting - just plain text
const MINIMAL_TOOLBAR_OPTIONS = {
  showBold: false,
  showItalic: false,
  showCode: false,
  showStrike: false,
  showHeadings: false,
  showLists: false,
  showCodeBlock: false,
  showBlockquote: false,
  showUndo: true,
  showRedo: true,
};

interface MinimalEditorProps extends Omit<BaseEditorProps, 'variant'> {
  // Additional props specific to minimal editor
  maxLength?: number;
  singleLine?: boolean;
}

export function MinimalEditor({
  maxLength,
  singleLine = false,
  ...props
}: MinimalEditorProps) {
  // TODO: Implement maxLength and singleLine constraints
  
  return (
    <TiptapEditor
      {...props}
      variant="minimal"
      enableToolbar={false}
      toolbarOptions={MINIMAL_TOOLBAR_OPTIONS}
      placeholder={props.placeholder || "Type here..."}
      className={`${props.className || ''} ${singleLine ? 'single-line' : ''}`}
    />
  );
}

export default MinimalEditor;