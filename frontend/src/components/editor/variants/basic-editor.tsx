"use client";

import React from 'react';
import { TiptapEditor } from '../tiptap-editor';
import { BaseEditorProps } from '@/lib/editor/editor-types';

// Basic editor with minimal formatting options
const BASIC_TOOLBAR_OPTIONS = {
  showBold: true,
  showItalic: true,
  showCode: false,
  showStrike: false,
  showHeadings: false,
  showLists: true,
  showCodeBlock: false,
  showBlockquote: false,
  showUndo: true,
  showRedo: true,
};

interface BasicEditorProps extends Omit<BaseEditorProps, 'variant'> {
  // Additional props specific to basic editor
  allowLists?: boolean;
  allowFormatting?: boolean;
}

export function BasicEditor({
  allowLists = true,
  allowFormatting = true,
  ...props
}: BasicEditorProps) {
  const toolbarOptions = {
    ...BASIC_TOOLBAR_OPTIONS,
    showBold: allowFormatting,
    showItalic: allowFormatting,
    showLists: allowLists,
  };

  return (
    <TiptapEditor
      {...props}
      variant="basic"
      toolbarOptions={toolbarOptions}
      placeholder={props.placeholder || "Start writing..."}
    />
  );
}

export default BasicEditor;