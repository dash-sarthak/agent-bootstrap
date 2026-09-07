---
name: web-design
description: Design system for the ToolBase web app. Use when creating or editing any page, layout, component, or print style in apps/web, or when reviewing UI changes.
---

# ToolBase design guideline

One page, one column, one rhythm. Every rule here exists to keep the site reading as a single, professionally typeset product instead of a pile of components. The readability audit (research/readability-audit-2026-09.md, `research/scripts/readability-audit/`) is the enforcement gate: any page change must keep both light and dark scores at 70 or above.

## Column

- The whole site lives in one `max-w-3xl` (48rem) column: header, main, and footer all use it. Never introduce a wider container on a page.
- Prose fills the column: there is no measure cap on paragraphs or list items. Never add `max-w-prose`, a ch/em cap, or a base-layer width rule to reading text; it runs to the `max-w-3xl` edge on every viewport.
- Long machine output (DNS records, CSV) uses `overflow-x-auto`, never page-level horizontal scroll.

## Spacing rhythm

- Hero section at the top of a page: `py-8`.
- Major sections after the hero: `mt-10` on the section, never `py-10` wrappers.
- Lists, FAQ stacks, and content under a section heading: `mt-3`.
- List items separate by `space-y-3` minimum (12px). `divide-y` rows may sit at any padding because the border is the separator.
- Inside cards: `space-y-4` between control groups, `gap-2` between label and field. Do not invent one-off margins.

## Type scale

| Role | Classes |
|---|---|
| h1 (one per page) | `text-3xl font-bold tracking-tight sm:text-4xl` |
| h2 (section) | `text-xl font-semibold tracking-tight` |
| h3 (FAQ question, sub-block) | `text-base font-semibold` |
| Body | `text-base` (16px) |
| Muted body, how-to steps, FAQ answers | `text-base text-muted-foreground` |
| Microcopy under 20 chars (buttons, dt terms, table headers, readouts) | `text-sm` or `text-xs` allowed |

- Reading text 20 characters or longer is never below 14px; long-form reading text is 16px.
- No italics anywhere. No italic font files ship, base CSS neutralizes `em/i/cite/var/dfn`, and `font-synthesis-style: none` blocks synthesis. Copy may mention the word italic (fancy-text tool) but must never style it.
- Fonts: SF Pro variable (self-hosted, latin subset, opsz axis) for everything; JetBrains Mono for machine output, textareas, and grids. Never load another family.

## Header and navigation

- The site header is sticky: `sticky top-0 z-40 border-b bg-background`, opaque, no backdrop blur, no scroll-triggered animation (NN/g, "Sticky Headers: 5 Ways to Make Them Better", nngroup.com/articles/sticky-headers: maximize content-to-chrome ratio, opaque background, minimal motion).
- The header carries the breadcrumb: site title in bold linking home, then `/ <page name>` on tool pages, then All tools on the right. There is no separate Home link. Breadcrumbs come from page metadata in `Base.astro` — pages must not render their own breadcrumb nav.
- Header height stays compact (`py-2.5`).

## Components

- Tool index rows: whole-row `<a>` with `aria-label` of the tool name, name `text-base font-semibold`, description `text-sm text-muted-foreground`, `divide-y divide-border border-y border-border` groups under an uppercase small `h2`.
- Category chips: `rounded-full border` pills with `aria-pressed` state.
- Buttons and inputs follow `packages/ui` and the island `TEXTAREA_CLASSES` pattern; do not restyle one-offs.
- Icons are decorative (`aria-hidden`) and never carry meaning alone.

## Dark mode

- Tokens only. Every text/background pair comes from the shadcn variables in `global.css`; no hardcoded colors except the light print reset and the compass dark variant.
- Dark palette must keep every pairing at WCAG AA (4.5:1) — verified by the audit, not by eye.

## Print

- The global `@media print` layer in `global.css` does the heavy lifting: pins `.dark` to light tokens (never remove that block), hides `header`, `footer`, `.no-print`, and ad units, strips `main` padding and max-width, and sets `@page { margin: 12mm }`. Per-page print style blocks are forbidden; extend the global layer instead.
- Mark interactive controls with `print:hidden` or `.no-print` and keep exactly one printable area per island. The printed sheet carries only the deliverable: no page title, no "Card N" labels, no hints, no buttons.
- Sheets size themselves to the page: bingo is two cards per row with dashed cut borders (`break-inside-avoid` per card, dashed outer border, `break-after-page` per row pair), word-search cells print at 7mm/10pt, tracing sheets fill the width with guide lines.
- Verify with print emulation (puppeteer `page.emulateMediaType('print')` + screenshot) before shipping any change to a printable.

## Before shipping any page change

1. `pnpm build` passes.
2. Readability audit re-run in both modes, both at 70+ (`research/scripts/readability-audit/`).
3. Zero computed italics, zero storage APIs, zero new network calls.
4. View-source still shows the full tool and content without JavaScript (seo-optimization skill).
