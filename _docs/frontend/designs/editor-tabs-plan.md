## Editor Tabs: Behavior and Implementation Plan

### Context
- Current implementation is custom: `EditorTabs`/`TabItem` via `TabBar`, styled with shadcn primitives (`Button`, `Tooltip`). No Radix Tabs/shadcn `Tabs` component is used.
- Relevant files:
  - `frontend/src/components/workspace/shared/TabBar.tsx`
  - `frontend/src/components/editor/tabs/EditorTabs.tsx`
  - `frontend/src/components/editor/tabs/components/TabItem.tsx`
  - `frontend/src/components/editor/tabs/components/NewTabButton.tsx`
  - `frontend/src/components/editor/tabs/hooks/useTabScroll.ts`
  - `frontend/src/components/editor/hooks/useEditorTabs.ts`
  - `frontend/src/components/workspace/shared/ContentAreaContainer.tsx`

Observations:
- Horizontal scroll is implemented, fade gradients exist, new tab button sits on the right, empty-state centers a “New Document” call-to-action.
- Tabs truncate with `max-w-[120px]`.
- Header container currently centers the `TabBar`, which causes the tab strip to appear centered rather than left-aligned across full width.

### Requirements
1) New document button sits on the far right; when there are no tabs, keep the centered “New Document” empty state.
2) Tabs should be left-aligned within a full-width header bar.
3) Each tab has a size limit and truncates gracefully.
4) The tab strip scrolls horizontally when overflowing.
5) Add a dropdown that lists all tabs (same visual language as a tab item) with basic search.
6) Hover shows the full path.
7) Labels should not show “.md” or any file-type prefix. These are not markdown files in UX.
8) Click-and-drag reordering on the tab strip and inside the “All tabs” list.

### Design
#### Data model
- Extend `Tab` to support full-path and a formatted display label.
  - `path?: string` – absolute or project-relative path used for tooltip/hover.
  - Do NOT persist extension in the displayed label. Derive `label` from `name` by stripping extension.

#### Rendering and layout
- Make the tab bar full-width and left-aligned:
  - Ensure `TabBar` root stretches (`w-full`).
  - Ensure `EditorTabs` root stretches (`w-full`) and hosts:
    - Left: horizontally scrollable tab list (`overflow-x-auto`, already present)
    - Right: controls (All Tabs dropdown, New Tab button).
  - Update `ContentAreaContainer` header alignment so editor header content is not force-centered. Add a prop to opt out of centering.

#### Label formatting
- Add a small utility `formatTabLabel(name: string)` that strips known extensions (e.g., `.md`, `.txt`, `.json`) and any accidental type prefixes.
- `TabItem` displays `formatTabLabel(tab.name)`.

#### Full path hover
- `TabItem` already uses `Tooltip`. Populate tooltip with `tab.path ?? tab.name` and keep the unsaved indicator.

#### Size limits and overflow
- Keep max width per tab; increase to `max-w-[160px]` for a little more room. Keep `truncate` and `whitespace-nowrap`.
- Horizontal scrolling is already implemented via `useTabScroll`.

#### All Tabs dropdown with search
- Add `AllTabsMenu` component placed at the right of the tab strip (before or after the New Tab button). Behavior:
  - Opens a dropdown listing all open tabs.
  - Each entry mirrors the `TabItem` visual language: label, unsaved dot, close affordance.
  - Clicking an entry activates the tab; clicking the close affordance closes it.
  - Include a lightweight search field to filter by label or path.
- Implementation options for search UI:
  - Simple: input field at top of dropdown + local `useState` filter.
  - Enhanced: integrate `cmdk` for better command palette-style search.
- Use shadcn `DropdownMenu` as the container. Render custom content inside its content area.

#### Drag-and-drop reordering
- Approach: add sortable DnD to both the horizontal tab strip and the vertical “All tabs” list.
- Library options:
  - `@dnd-kit` (recommended for flexibility) – `SortableContext` with `horizontalListSortingStrategy` for the strip; default vertical strategy for the list.
  - `@hello-pangea/dnd` (react-beautiful-dnd maintained fork) – simple list reordering horizontally/vertically.
  - Simpler wrappers like `react-sortablejs` can also work.
- Note on dropdowns: dragging inside `DropdownMenu` can conflict with its dismissal behavior. If this becomes an issue, render the “All tabs” panel using `Popover` or `Dialog` instead when entering “Reorder mode,” keeping `DropdownMenu` for quick search/select.

### Implementation Steps
1) Types
   - Edit `frontend/src/components/editor/tabs/types.ts`:
     - Add `path?: string` to `Tab`.

2) Label formatting utility
   - Add `frontend/src/components/editor/tabs/utils/labels.ts` with `formatTabLabel(name: string): string`.
   - Update `TabItem` to render `formatTabLabel(tab.name)`.

3) Tooltip full path
   - Update `TabItem` tooltip content to show `tab.path || tab.name` (retain unsaved note and middle-click hint).

4) Width and alignment
   - In `TabBar` (advanced mode container) and `EditorTabs`, add `w-full` to stretch across the header.
   - In `ContentAreaContainer`, add a prop `centerHeader?: boolean` (default `true`).
   - In `EditorPanel`, pass `centerHeader={false}` so tabs are not centered and can align to left/right as designed.

5) All Tabs menu
   - Create `frontend/src/components/editor/tabs/components/AllTabsMenu.tsx` using shadcn `DropdownMenu`.
   - Render a searchable list of all tabs. Use a small shared subcomponent to keep visuals consistent with `TabItem` (reuse inner label and unsaved dot styling).
   - Place the menu trigger at the far right of the tab bar, left of the New Tab button (New remains rightmost) or to its left depending on spacing.
   - Keyboard: optional follow-up (e.g., `⌘/` to open menu) – out-of-scope for first pass.

6) Tuning
   - Increase per-tab max width to `max-w-[160px]` in `TabItem` and keep `truncate`.

7) QA and polish
   - Verify:
     - Empty state stays centered and reads “New Document”.
     - Adding a tab appends to the right and selects it.
     - Tabs left-align; controls stay at far right.
     - Overflow fades and horizontal scroll works with trackpad/mouse.
     - Dropdown lists every tab, filters by label/path, can select and close.
     - Tooltip shows full path.

8) Drag-and-drop reordering
   - Add `reorderTabs(fromIndex: number, toIndex: number)` to `useEditorTabs` and export it.
   - Horizontal strip: wrap the tab list in DnD provider and sortable context; make each `TabItem` a draggable/sortable item; on drag end, call `reorderTabs` and preserve `activeTabId`.
   - All Tabs list: inside the dropdown (or a `Popover` in reorder mode), render a sortable vertical list with the same ids; on drag end, call `reorderTabs`.
   - Ensure scrolling works while dragging (auto-scroll or allow manual horizontal scroll under the pointer).

### Nice-to-haves (later)
- Keyboard shortcuts: cycle tabs, close active (`⌘W`), show dropdown/command menu (`⌘K` or `⌘/`).
- Persist/reopen last session’s tabs.
- Drag-reorder tabs.

### Alternatives considered
- Keep custom (chosen): minimal churn, integrates with Tailwind/shadcn.
- `rc-tabs` – built-in overflow dropdown and closable tabs. Styling alignment with our design may require overrides. Reference: [rc-tabs](https://github.com/react-component/tabs).
- Radix Tabs + ScrollArea – accessible primitives; requires wiring overflow and dropdown. References: [Radix Tabs](https://www.radix-ui.com/primitives/docs/components/tabs), [Radix ScrollArea](https://www.radix-ui.com/primitives/docs/components/scroll-area).
- Search UI: [cmdk](https://cmdk.paco.me/) for palette-like search.
- Drag and drop libraries: [react-beautiful-dnd](https://github.com/atlassian/react-beautiful-dnd) (archived), maintained fork [@hello-pangea/dnd](https://github.com/hello-pangea/dnd), [react-sortablejs](https://github.com/risingstack/react-sortablejs).

### References
- Prior work for inspiration (test branch): [haowjy/shuscribe test branch components](https://github.com/haowjy/shuscribe/tree/test/frontend/src/components)
- Overflow/closable tabs library: [rc-tabs](https://github.com/react-component/tabs)
- Radix primitives: [Tabs](https://www.radix-ui.com/primitives/docs/components/tabs), [ScrollArea](https://www.radix-ui.com/primitives/docs/components/scroll-area)
- shadcn DropdownMenu: [docs](https://ui.shadcn.com/docs/components/dropdown-menu)
- Search palette: [cmdk](https://cmdk.paco.me/)


