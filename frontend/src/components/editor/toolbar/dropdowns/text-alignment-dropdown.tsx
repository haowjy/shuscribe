'use client'

import React from 'react'
import { ChevronDown } from 'lucide-react'
import { OptionsDropdown } from '../primitives/options-dropdown'
import { TEXT_ALIGNMENT_OPTIONS } from '../../utils/editor-constants'
import { executeEditorCommand, createDropdownCloseHandler } from '../../utils/editor-helpers'
import type { TextAlignmentDropdownProps } from '../../types/editor.types'

export const TextAlignmentDropdown = React.memo<TextAlignmentDropdownProps>(({ 
  editor, 
  editorState: _,
  currentTextAlignment,
  textAlignmentOpen,
  setTextAlignmentOpen,
}) => {
  const CurrentAlignIcon = currentTextAlignment.icon
  const closeHandler = React.useMemo(() => editor ? createDropdownCloseHandler(editor) : undefined, [editor])

  const options = React.useMemo(() => 
    TEXT_ALIGNMENT_OPTIONS.map((option) => ({
      id: option.id,
      label: option.label,
      icon: option.icon,
      onSelect: () => editor && executeEditorCommand(editor, option.command, { value: option.value })
    })), [editor])

  if (!editor) return null

  return (
    <OptionsDropdown
      trigger={
        <div className="flex items-center gap-2">
          <CurrentAlignIcon size={16} />
          <span className="text-sm">{currentTextAlignment.label}</span>
          <ChevronDown size={12} className="ml-2 flex-shrink-0" />
        </div>
      }
      tooltip="Text Alignment"
      open={textAlignmentOpen}
      onOpenChange={setTextAlignmentOpen}
      className="w-auto px-3 justify-between whitespace-nowrap"
      contentClassName="w-[130px]"
      onCloseAutoFocus={closeHandler}
      options={options}
    />
  )
})

TextAlignmentDropdown.displayName = 'TextAlignmentDropdown'