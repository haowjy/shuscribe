'use client'

import React from 'react'
import { Button } from '@/components/tiptap-ui-primitive/button'
import { DynamicFormatButton } from './primitives/dynamic-format-button'
import { ToolbarGroups } from './primitives/toolbar-groups'
import { ToolbarButtonGroup } from './primitives/toolbar-button-group'
import { TextStyleDropdown } from './dropdowns/text-style-dropdown'
import { TextAlignmentDropdown } from './dropdowns/text-alignment-dropdown'
import { SpecialFormattingDropdown } from './dropdowns/special-formatting-dropdown'
import { TableDropdown } from './dropdowns/table-dropdown'
import { TOOLBAR_BUTTONS, SPECIAL_FORMATTING_OPTIONS } from '../utils/editor-constants'
import { Image as ImageIcon } from 'lucide-react'
import { executeEditorCommand, triggerImageUpload, handleImageUpload } from '../utils/editor-helpers'
import type { EditorToolbarProps, EditorCommand, ToolbarSection } from '../types/editor.types'

export const EditorToolbar = React.memo<EditorToolbarProps>(({ 
  editor, 
  editorState,
  toolbarState,
  config = {},
}) => {
  const {
    textStyleOpen,
    setTextStyleOpen,
    textAlignmentOpen,
    setTextAlignmentOpen,
    specialFormattingOpen,
    setSpecialFormattingOpen,
    tableOpen,
    setTableOpen,
    currentTextStyle,
    currentTextAlignment,
  } = toolbarState

  // Helper to check if a section should be shown
  const isSectionShown = React.useCallback((sectionName: string) => {
    // If no sections specified, show all sections
    if (!config.sections) return true
    return config.sections.includes(sectionName as ToolbarSection)
  }, [config.sections])

  // Helper to check if a command should be shown
  const isCommandShown = React.useCallback((command: string) => {
    // If no commands specified, show all commands
    if (!config.commands) return true
    return config.commands.includes(command as EditorCommand)
  }, [config.commands])

  // Memoized event handlers for performance
  const handleImageUploadClick = React.useCallback(() => {
    // TODO: replace handleImageUpload with real upload logic when backend is ready
    if (editor) {
      triggerImageUpload(editor, handleImageUpload)
    }
  }, [editor])

  const createCommandHandler = React.useCallback((command: EditorCommand, params?: unknown) => {
    return () => {
      if (editor) {
        executeEditorCommand(editor, command, params as never)
      }
    }
  }, [editor])

  if (!editor) return null

  return (
    <div className="border-b border-border bg-background p-2">
      <div className="flex items-center gap-1 overflow-x-auto pb-1 toolbar-scroll">
        <ToolbarGroups>
          {/* History Section */}
          {isSectionShown('history') && (
            <ToolbarButtonGroup
              buttons={TOOLBAR_BUTTONS.history}
              editorState={editorState}
              isCommandShown={isCommandShown}
              createCommandHandler={createCommandHandler}
            />
          )}

          {/* Text Style Dropdown */}
          {isSectionShown('textStyle') && (
            <TextStyleDropdown
              editor={editor}
              editorState={editorState}
              currentTextStyle={currentTextStyle}
              textStyleOpen={textStyleOpen}
              setTextStyleOpen={setTextStyleOpen}
            />
          )}

          {/* Basic Formatting Section */}
          {isSectionShown('formatting') && (
            <>
              <ToolbarButtonGroup
                buttons={TOOLBAR_BUTTONS.formatting}
                editorState={editorState}
                isCommandShown={isCommandShown}
                createCommandHandler={createCommandHandler}
              />

              {/* Dynamic Format Buttons - only show when active */}
              {SPECIAL_FORMATTING_OPTIONS.filter(option => option.id !== 'codeBlock').map((option) => {
                const isActive = option.stateKey ? (editorState?.[option.stateKey] || false) : false
                
                if (!isCommandShown(option.command)) return null;
                
                return (
                  <DynamicFormatButton
                    key={option.id}
                    isActive={isActive}
                    command={createCommandHandler(option.command)}
                    icon={option.icon}
                    tooltip={option.label}
                  />
                )
              })}

              {/* Special Formatting Dropdown */}
              <SpecialFormattingDropdown
                editor={editor}
                editorState={editorState}
                specialFormattingOpen={specialFormattingOpen}
                setSpecialFormattingOpen={setSpecialFormattingOpen}
              />
            </>
          )}

          {/* Lists Section */}
          {isSectionShown('lists') && (
            <ToolbarButtonGroup
              buttons={TOOLBAR_BUTTONS.lists}
              editorState={editorState}
              isCommandShown={isCommandShown}
              createCommandHandler={createCommandHandler}
            />
          )}

          {/* Text Alignment Dropdown */}
          {isSectionShown('alignment') && (
            <TextAlignmentDropdown
              editor={editor}
              editorState={editorState}
              currentTextAlignment={currentTextAlignment}
              textAlignmentOpen={textAlignmentOpen}
              setTextAlignmentOpen={setTextAlignmentOpen}
            />
          )}

          {/* Blocks Section */}
          {isSectionShown('blocks') && (
            <ToolbarButtonGroup
              buttons={TOOLBAR_BUTTONS.blocks}
              editorState={editorState}
              isCommandShown={isCommandShown}
              createCommandHandler={createCommandHandler}
            />
          )}

          {/* Insert Section */}
          {isSectionShown('insert') && (
            <>
              {isCommandShown('uploadImage') && (
                <Button
                  onClick={handleImageUploadClick}
                  data-size="toolbar"
                  tooltip="Upload Image"
                >
                  <ImageIcon size={16} />
                </Button>
              )}
              {isCommandShown('setHorizontalRule') && (
                <Button
                  onClick={createCommandHandler('setHorizontalRule')}
                  data-size="toolbar"
                  tooltip="Horizontal Rule"
                >
                  {React.createElement(TOOLBAR_BUTTONS.insert[0].icon, { size: 16 })}
                </Button>
              )}
            </>
          )}

          {/* Table Dropdown */}
          {isSectionShown('table') && (
            <TableDropdown
              editor={editor}
              editorState={editorState}
              tableOpen={tableOpen}
              setTableOpen={setTableOpen}
            />
          )}
        </ToolbarGroups>
      </div>
    </div>
  )
})

EditorToolbar.displayName = 'EditorToolbar'