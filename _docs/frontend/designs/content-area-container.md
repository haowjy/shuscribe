# ContentAreaContainer Pattern

## Overview

The ContentAreaContainer provides a reusable layout pattern with integrated sidebar controls, consistent header/footer structure, and conditional toggle button behavior. This pattern ensures consistent user interface across different content types while handling sidebar state management.

## Design Pattern

### Purpose and Benefits

**Consistency**: Uniform header/footer structure across components with consistent toggle button behavior and standardized sidebar integration patterns.

**Flexibility**: Optional header, footer, and sidebar configurations with customizable content in all sections and responsive layout handling.

**Reusability**: Single component handles multiple layout scenarios with consistent API across different content types, making it easy to integrate with existing components.

**User Experience**: Predictable toggle button placement with tooltips, keyboard shortcuts, and accessible button implementations.

### Core Architecture

The container provides a three-section layout structure:
- **Header Section**: Optional header content with conditional sidebar toggle buttons
- **Main Content**: Flexible content area with proper overflow handling  
- **Footer Section**: Optional footer content with bottom panel toggle support

**Key Implementation Details**: See `ContentAreaContainer` in `frontend/src/components/ui/ContentAreaContainer.tsx`

## Component Interface

### Props Structure

**Primary Interface**: See `ContentAreaContainerProps` in `frontend/src/components/ui/ContentAreaContainer.tsx`

**Core Configuration**:
- `headerContent`, `footerContent`: Optional React nodes for header/footer sections
- `leftSidebar`, `rightSidebar`, `bottomPanel`: Sidebar control objects with state and handlers
- `children`: Main content area
- `className`: Additional styling

**Sidebar Control Pattern**: Each sidebar control contains `isOpen` state, `onToggle` handler, optional `label` and `shortcut` for tooltips.

### Toggle Button Behavior

**Conditional Visibility**: Toggle buttons only appear when their corresponding sidebar is collapsed, ensuring clean interface when panels are open.

**Implementation**: See toggle button components in `frontend/src/components/ui/ContentAreaContainer.tsx:HeaderToggleButton()` and `FooterToggleButton()`

## Integration Patterns

### Editor Panel Integration

**Primary Usage**: EditorPanel uses ContentAreaContainer for consistent layout across the editor workspace.

**Implementation**: See `EditorPanel` in `frontend/src/components/editor/EditorPanel.tsx` for complete integration pattern including:
- Header content with TabBar for editor tabs
- Sidebar configurations for file explorer and AI chat
- Main editor content area with DocumentEditor

### Workspace Layout Integration

**State Management**: WorkspaceLayout passes sidebar state from ProjectStateProvider to EditorPanel via ContentAreaContainer props.

**Integration Pattern**: See `WorkspaceLayout.renderContent()` in `frontend/src/components/workspace/layout/WorkspaceLayout.tsx`

## Configuration Patterns

### Layout Flexibility

**Optional Elements**: All sections (header, footer, sidebars) render conditionally based on provided props.

**Responsive Behavior**: Header uses flexbox for varying content sizes, main content handles overflow with `min-h-0` pattern.

**Panel State**: Integration with react-resizable-panels for collapsible behavior and state persistence.

### Customization Options

**Toggle Icons**: Different content types can use appropriate icons (file explorer, chat interface, terminal).

**Footer Content**: Support for various footer content types (word counts, status indicators, auto-save information).

**Sidebar Controls**: Flexible sidebar configuration supporting different panel types and keyboard shortcuts.

## Extension Points

### Future Enhancements

The pattern is designed to support:
- Additional panel positions (top panel, multiple sidebars)
- Custom toggle button animations and interactions
- Advanced responsive behavior for mobile layouts
- Integration with collaborative editing features

### Component Architecture

**Implementation Files**:
- Main component: `frontend/src/components/ui/ContentAreaContainer.tsx`
- Usage patterns: `frontend/src/components/editor/EditorPanel.tsx`
- Integration: `frontend/src/components/workspace/layout/WorkspaceLayout.tsx`

This pattern provides the foundation for consistent workspace layouts across the ShuScribe interface while maintaining flexibility for different content types and use cases.