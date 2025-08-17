// Panel size constants
export const PANEL_SIZES = {
  LEFT_SIDEBAR: {
    default: 20,
    min: 12,
    max: 40
  },
  RIGHT_SIDEBAR: {
    default: 20,
    min: 12,
    max: 40
  },
  BOTTOM_PANEL: {
    default: 20,
    min: 12,
    max: 80
  },
  EDITOR: {
    default: 75,
    min: 20
  },
  MIDDLE_SECTION: {
    default: 50,
    min: 30
  }
} as const

// Keyboard shortcuts
export const SHORTCUTS = {
  TOGGLE_LEFT: 'b',
  TOGGLE_RIGHT: '\\',
  TOGGLE_BOTTOM: 'j',
  SETTINGS: ','
} as const

// Panel IDs for resizable panels
export const PANEL_IDS = {
  LEFT_SIDEBAR: 'left-sidebar',
  RIGHT_SIDEBAR: 'right-sidebar',
  BOTTOM_PANEL: 'bottom-panel',
  EDITOR: 'editor',
  MIDDLE_SECTION: 'middle-section'
} as const