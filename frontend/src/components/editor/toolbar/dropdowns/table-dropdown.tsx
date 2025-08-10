'use client'

import React from 'react'
import { ChevronDown, Table as TableIcon } from 'lucide-react'
import { OptionsDropdown } from '../primitives/options-dropdown'
import { TABLE_OPTIONS } from '../../utils/editor-constants'
import { executeEditorCommand, createDropdownCloseHandler } from '../../utils/editor-helpers'
import type { TableDropdownProps } from '../../types/editor.types'

export const TableDropdown = React.memo<TableDropdownProps>(({ 
  editor, 
  editorState: _,
  tableOpen,
  setTableOpen,
}) => {
  const closeHandler = React.useMemo(() => editor ? createDropdownCloseHandler(editor) : undefined, [editor])

  const options = React.useMemo(() => 
    TABLE_OPTIONS.map((option) => ({
      id: option.id,
      label: option.label,
      icon: option.icon,
      onSelect: () => {
        if (!editor) return
        if ('params' in option && option.params) {
          executeEditorCommand(editor, option.command, option.params)
        } else {
          executeEditorCommand(editor, option.command)
        }
      },
      className: ('variant' in option) && option.variant === "destructive" ? "text-destructive" : undefined
    })), [editor])

  if (!editor) return null

  return (
    <OptionsDropdown
      trigger={
        <>
          <TableIcon size={16} />
          <ChevronDown size={12} className="ml-1 flex-shrink-0" />
        </>
      }
      tooltip="Table"
      open={tableOpen}
      onOpenChange={setTableOpen}
      className="w-auto px-2"
      contentClassName="w-[180px]"
      onCloseAutoFocus={closeHandler}
      options={options}
    />
  )
})

TableDropdown.displayName = 'TableDropdown'