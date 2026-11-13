# {{PROJECT_NAME}} — Design System

Source of truth for every screen. Components live in `packages/ui`; tokens are CSS variables consumed by Tailwind.

## 1. Principles

<!-- AUTO: 3–5 principles tied to the users, e.g. "Fast at the counter: every frequent action is one tap" for a restaurant POS. -->

## 2. Design tokens

All colours are defined for light and dark themes and meet WCAG 2.2 AA contrast (4.5:1 text, 3:1 large text and UI).

### Colour

| Token | Light | Dark | Use |
|---|---|---|---|
<!-- AUTO: background, surface, surface-muted, border, text, text-muted, primary, primary-foreground, secondary, accent, success, warning, danger, info, focus-ring. Give hex values and checked contrast. -->

### Typography

<!-- AUTO: font families with fallback stacks; scale (xs → 4xl) with size/line-height/weight; numeric tabular figures for tables and money. -->

### Spacing, radius, elevation, motion

<!-- AUTO: 4px base spacing scale; radius sm/md/lg/full; 3 shadow levels; durations (100/200/300 ms) and easing; respect prefers-reduced-motion. -->

### Breakpoints

<!-- AUTO: sm/md/lg/xl/2xl and which layouts change at each. -->

## 3. Components

For each: purpose, variants, sizes, states (default, hover, focus-visible, active, disabled, loading, error), accessibility notes.

<!-- AUTO: Button, IconButton, Input, Textarea, Select, Combobox, Checkbox, Radio, Switch, DatePicker, FileUpload, Form field (label + help + error), DataTable (sort, filter, paginate, row actions, bulk actions, empty state), Card, StatCard, Badge/Status pill, Tabs, Modal, Drawer, Toast, Tooltip, Dropdown menu, Breadcrumbs, Pagination, Skeleton, EmptyState, ErrorState, ConfirmDialog (for destructive actions), Avatar, Chart wrappers, QR/Barcode if needed. -->

## 4. Layout patterns

- **Panel shell** (admin and other role panels): collapsible sidebar navigation, top bar with search, notifications, profile menu; content max-width; responsive drawer on mobile.
- **List page**: title + primary action, filters bar, DataTable, pagination; loading skeleton, empty state with call to action, error state with retry.
- **Detail page**: header with status and actions, tabs for sections, activity/audit timeline.
- **Form page**: single column, grouped sections, inline validation, sticky save bar, unsaved-changes guard.
- **Dashboard**: KPI stat cards, charts, recent activity, quick actions.
- **Public pages**: <!-- AUTO: landing / listing / booking pages if the product has a public side. -->

## 5. Role panels

| Panel | Route prefix | Primary colour accent | Navigation items |
|---|---|---|---|
<!-- AUTO: one row per role panel so users always know which panel they are in. -->

## 6. Accessibility rules

- Every input has a visible label; errors are announced (`aria-live`) and linked with `aria-describedby`.
- All actions reachable by keyboard; visible focus ring from the `focus-ring` token; logical tab order; skip link.
- Modals trap focus and restore it on close; Escape closes.
- Never use colour alone to convey status; pair with icon or text.
- Touch targets at least 24×24 CSS px (44×44 preferred on mobile).
- Images have alt text; decorative images use empty alt.

## 7. Content and voice

<!-- AUTO: tone, button verb style ("Save event" not "Submit"), date/time/currency formats, error message pattern (what happened + how to fix). -->

## 8. Implementation mapping

<!-- AUTO: where tokens live (CSS variables file), Tailwind theme extension, component library base (e.g. shadcn/ui primitives), icon set, chart library. -->
