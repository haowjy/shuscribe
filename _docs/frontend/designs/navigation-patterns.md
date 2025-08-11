# Navigation Patterns

## Design Philosophy

**Core Principle**: Respects creative workflow patterns - writers focus deeply on single projects rather than rapidly switching between universes.

**Research Insight**: Creative professionals prefer single-project focus vs multi-project juggling. Deep work requires sustained attention on one creative context, unlike developers who frequently switch between codebases.

## Navigation Strategy

### Current Implementation

- **Landing Page (`/`)**: Marketing header with branding/auth
- **Projects Page (`/projects`)**: Global activity rail + headless content area for clean project selection  
- **Future Workspace (`/projects/[id]`)**: Rail + project sidebar for file/document navigation within selected project

### Navigation Patterns

- **Global Activity Rail**: VSCode-inspired 56px fixed rail with app-wide actions (Home, Search, AI, Help, Settings)
- **Mobile Floating Dock**: Rail becomes compact floating dock on mobile screens for better usability
- **No Project Switching in Workspace**: Users commit to a creative universe for extended work sessions
- **Clean Project Selection**: Focus on deliberate project choice without navigation clutter
- **Context-Appropriate Sidebars**: Different sidebar purposes based on user context and needs
- **Future Command Palette**: Cmd+K for power users who need quick actions across contexts
- **Keyboard Shortcuts**: ⌘, opens settings modal from any app route

## User Interface Consistency

### Layout Structure
- **Global Activity Rail**: Persistent 56px rail on all app routes (`/projects/*`)
- **Settings Access**: Gear icon in rail provides consistent access to account/settings across all contexts
- **Breadcrumb Navigation**: `← Projects / Project Name` pattern within workspace content area
- **No Position Switching**: Global actions remain in fixed rail location to avoid jarring transitions

### Layout Patterns
- **Landing Page**: Marketing header only, no rail
- **Projects Page**: Rail + headless content area focusing on project selection
- **Future Workspace**: Rail + project sidebar + main content (breadcrumb within main area)
- **Separation of Concerns**: Rail for app-level actions, project sidebar for context-specific navigation

## User Experience Flow

### Projects Page (`/projects`)
```
┌─┬───────────────────────────────────────────────────────┐
│⌂│ Projects                                              │
│⌕├───────────────────────────────────────────────────────┤
│✦│                                                       │
│ │ [Search projects...]                    [New Project] │
│?│                                                       │
│⚙│ ┌───────────────────────────────────────────────────┐ │
│ │ │ ● Project Name                       Time ago     │ │
│ │ │   Description...                                  │ │
│ │ │   Stats • Status                      [tag]       │ │
│ │ └───────────────────────────────────────────────────┘ │
└─┴───────────────────────────────────────────────────────┘
```

**Features:**
- Global activity rail with Home, Search, AI, Help, Settings
- Clean project list for deliberate selection  
- Settings modal accessible via rail gear icon
- Search functionality wired to rail search icon
- Mobile: Rail becomes floating dock in bottom-right

### Project Workspace (`/projects/[id]`)
```
┌─┬───────────────┬─────────────────────────────────────────┐
│⌂│               │ ← Projects / Project Name                │
│⌕│ 📁 Characters │                                         │
│✦│   └ Name       │ # Document Title                        │
│ │               │                                         │
│?│ 📁 Locations  │ Content editor...                       │
│⚙│   └ Place     │                                         │
│ │               │                                         │
│ │ 📝 Documents  │                                         │
│ │   ● Chapter 1 │                                         │
│ │   ● Chapter 2 │                                         │
└─┴───────────────┴─────────────────────────────────────────┘
```

**Features:**
- Global activity rail consistent with projects page
- Breadcrumb navigation back to projects within main content
- Project sidebar focused on file/document navigation within project
- Settings accessible via rail gear icon
- No project switching - committed workspace experience

## Settings Strategy

### Rail-Based Settings Access
- **Profile Information**: Displayed in settings modal with user avatar and email
- **Settings Modal**: Global app preferences (theme, account, shortcuts, etc.)
- **Help & Support**: Accessible via dedicated help icon in rail
- **Sign Out**: Available in settings modal
- **Keyboard Shortcut**: ⌘, opens settings from any app route

### Implementation Rationale
- **Global Activity Rail**: Consistent placement across all app routes
- **Always Accessible**: Settings gear icon available from any context
- **Headless Design**: Maintains clean, distraction-free project selection
- **Mobile Optimized**: Settings accessible via floating dock on small screens

## Future Enhancements

### Command Palette
- **Trigger**: Cmd+K for power users
- **Functionality**: Quick actions across contexts
- **Use Cases**: Search, navigation, project actions

### Settings Integration
- **Modal/Page**: Triggered from UserDropdown
- **Global Scope**: App-level preferences, not project-specific
- **Categories**: Theme, account, shortcuts, integrations

## Design Decisions Log

### Research-Based Decisions
- **No Rapid Project Switching**: Based on creative workflow research
- **Headless Projects Page**: Clean focus on project selection
- **Consistent Header**: Prevents jarring user experience transitions

### Anti-Patterns Avoided
- **Context-Switching Sidebars**: Would be counter-intuitive
- **Project Switcher in Workspace**: Unnecessary for creative workflows  
- **Moving UI Elements**: Maintains predictable user experience

## Implementation Status

### Completed Components
- **`GlobalActivityRail`**: VSCode-inspired 56px rail with responsive mobile dock
- **`AppLayoutWithRail`**: Layout wrapper that conditionally shows rail on app routes
- **`SettingsModal`**: Modal-based settings with account, preferences, help, and sign-out
- **Keyboard Shortcuts**: ⌘, shortcut for settings access
- **Mobile Responsive**: Floating dock design for smaller screens
- **Accessibility**: Full ARIA labels, keyboard navigation, focus management

### Integration Points
- **Layout Integration**: Rail shows on `/projects/*` routes, hidden on landing page
- **Search Integration**: Rail search icon focuses existing search input on projects page
- **Settings Access**: Replaces previous UserDropdown with modal-based approach
- **User Authentication**: Integrates with existing Supabase auth context

### Future Implementation
- **Command Palette**: ⌘K shortcut for advanced user actions
- **Workspace Sidebar**: Project-specific file navigation for `/projects/[id]` routes
- **Help Integration**: Connect help icon to documentation system