'use client'

import React from 'react'
import { Button } from '@/components/tiptap-ui-primitive/button'
import type { ToolbarButtonConfig, EditorState, EditorCommand } from '../../types/editor.types'

export interface ToolbarButtonGroupProps {
  buttons: readonly ToolbarButtonConfig[]
  editorState: EditorState | null
  isCommandShown: (command: string) => boolean
  createCommandHandler: (command: EditorCommand, params?: unknown) => () => void
}

export const ToolbarButtonGroup = React.memo<ToolbarButtonGroupProps>(({
  buttons,
  editorState,
  isCommandShown,
  createCommandHandler,
}) => {
  return (
    <>
      {buttons
        .filter((button) => isCommandShown(button.command))
        .map((button) => {
          const ButtonIcon = button.icon
          const isActive = button.stateKey ? (editorState?.[button.stateKey] || false) : false
          
          return (
            <Button
              key={button.id}
              onClick={createCommandHandler(button.command)}
              data-active-state={isActive ? "on" : "off"}
              tooltip={button.tooltip}
              shortcutKeys={button.shortcutKeys}
            >
              <ButtonIcon size={16} />
            </Button>
          )
        })}
    </>
  )
})

ToolbarButtonGroup.displayName = 'ToolbarButtonGroup'
