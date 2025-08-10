'use client'

import React from 'react'
import { ChevronDown, MoreHorizontal } from 'lucide-react'
import { OptionsDropdown } from '../primitives/options-dropdown'
import { SPECIAL_FORMATTING_OPTIONS } from '../../utils/editor-constants'
import { executeEditorCommand, createDropdownCloseHandler, shouldHideSpecialFormattingOption } from '../../utils/editor-helpers'
import type { SpecialFormattingDropdownProps } from '../../types/editor.types'

export const SpecialFormattingDropdown = React.memo<SpecialFormattingDropdownProps>(({ 
  editor, 
  editorState,
  specialFormattingOpen,
  setSpecialFormattingOpen,
}) => {
  const closeHandler = React.useMemo(() => editor ? createDropdownCloseHandler(editor) : undefined, [editor])

  // Filter out options that are currently active (should be shown in main toolbar)
  const visibleOptions = React.useMemo(() => {
    return SPECIAL_FORMATTING_OPTIONS.filter(option => {
      // Always show code block as it's not in the dynamic buttons
      if (option.id === 'codeBlock') return true
      
      // Hide options that are currently active
      return !shouldHideSpecialFormattingOption(option.stateKey, editorState)
    })
  }, [editorState])

  const options = React.useMemo(() => 
    visibleOptions.map((option) => ({
      id: option.id,
      label: option.label,
      icon: option.icon,
      onSelect: () => editor && executeEditorCommand(editor, option.command)
    })), [editor, visibleOptions])

  if (!editor) return null

  return (
    <OptionsDropdown
      trigger={
        <>
          <MoreHorizontal size={16} />
          <ChevronDown size={12} className="ml-1 flex-shrink-0" />
        </>
      }
      tooltip="Special Formatting"
      open={specialFormattingOpen}
      onOpenChange={setSpecialFormattingOpen}
      className="w-auto px-2"
      contentClassName="w-[160px]"
      onCloseAutoFocus={closeHandler}
      options={options}
    />
  )
})

SpecialFormattingDropdown.displayName = 'SpecialFormattingDropdown'