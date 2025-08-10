'use client'

import React from 'react'
import { ChevronDown } from 'lucide-react'
import { OptionsDropdown } from '../primitives/options-dropdown'
import { TEXT_STYLE_OPTIONS } from '../../utils/editor-constants'
import { executeEditorCommand, createDropdownCloseHandler } from '../../utils/editor-helpers'
import type { TextStyleDropdownProps } from '../../types/editor.types'

export const TextStyleDropdown = React.memo<TextStyleDropdownProps>(({ 
  editor, 
  editorState: _,
  currentTextStyle,
  textStyleOpen,
  setTextStyleOpen,
}) => {
  const CurrentStyleIcon = currentTextStyle.icon
  const closeHandler = React.useMemo(() => editor ? createDropdownCloseHandler(editor) : undefined, [editor])

  const options = React.useMemo(() => 
    TEXT_STYLE_OPTIONS.map((option) => ({
      id: option.id,
      label: option.label,
      icon: option.icon,
      onSelect: () => {
        if (!editor) return
        if (option.level) {
          executeEditorCommand(editor, option.command, { level: option.level })
        } else {
          executeEditorCommand(editor, option.command)
        }
      }
    })), [editor])

  if (!editor) return null

  return (
    <OptionsDropdown
      trigger={
        <div className="flex items-center gap-2">
          <CurrentStyleIcon size={16} />
          <span className="text-sm">{currentTextStyle.label}</span>
          <ChevronDown size={12} className="ml-2 flex-shrink-0" />
        </div>
      }
      tooltip="Text Style"
      open={textStyleOpen}
      onOpenChange={setTextStyleOpen}
      className="w-auto px-3 justify-between whitespace-nowrap"
      contentClassName="w-[140px]"
      onCloseAutoFocus={closeHandler}
      options={options}
    />
  )
})

TextStyleDropdown.displayName = 'TextStyleDropdown'