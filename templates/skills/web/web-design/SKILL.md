---
name: web-design
description: Design system rules for a web UI. Use when creating or editing any page, layout, component, or print style, or when reviewing UI changes.
---

# Web design guideline

One page, one column, one rhythm. Every rule here exists to keep the site reading as a single, professionally typeset product instead of a pile of components. Adopt the rules as written, then pin the project's own values (the column width, the scale steps, the font families) in the first section so there is one place to look them up.

Pair this skill with a measured readability and contrast audit. Set a numeric floor, run it in both light and dark mode, and treat it as a merge gate rather than a suggestion.

## Column

- The whole site lives in one reading column: header, main, and footer all use it. Never introduce a wider container for a single page.
- Prose fills the column. Do not add a second, narrower measure cap on paragraphs or list items; reading text runs to the column edge on every viewport.
- Long machine output (tables, logs, DNS records, CSV) scrolls inside its own container. The page body never scrolls horizontally.

## Spacing rhythm

- Pick one spacing scale and give each role exactly one step: hero block, section after the hero, content under a heading, gap between list items, gap inside a card, gap between a label and its field.
- Write those roles down once and reuse them. A one-off margin is a bug; if a case genuinely needs a new value, add it to the scale under a name.
- Separated rows are the exception: where a border already divides items, the padding is free to differ from the list step.

## Type scale

- One h1 per page. Section and sub-block headings each get one declared size and weight, and nothing else invents a size.
- Body copy is 16px. Reading text of 20 characters or more never drops below 14px. Short microcopy (buttons, table headers, numeric readouts) may go smaller.
- Decide the italic policy explicitly. If the project ships no italic face, neutralize `em`, `i`, `cite`, `var`, and `dfn` in the base layer and set `font-synthesis-style: none` so the browser cannot fake one. Copy may name italics without styling them.
- Name the families once: one for interface and prose, one monospace for machine output, textareas, and grids. Never load a third.

## Header and navigation

- The site header is sticky and opaque. No backdrop blur, no scroll-triggered animation, no height change on scroll. Maximize the content-to-chrome ratio and keep motion out of it (NN/g, "Sticky Headers: 5 Ways to Make Them Better", nngroup.com/articles/sticky-headers).
- The header carries the breadcrumb, and breadcrumbs come from page metadata in the layout. A page never renders its own breadcrumb nav, or the two drift.
- Keep the header compact. It is navigation, not a banner.

## Components

- A row that links somewhere is one whole-row anchor with an accessible label, not a title link with dead space around it.
- Toggle chips carry `aria-pressed`. Any control with state exposes that state to assistive technology.
- Buttons and inputs come from the shared component layer. Restyling one instance is how a design system dies.
- Icons are decorative (`aria-hidden`) and never carry meaning alone.

## Dark mode

- Tokens only. Every text and background pair resolves through declared variables. No hardcoded colors, with a documented exception list if the project needs one.
- Every pairing holds WCAG AA contrast (4.5:1 for body text, 3:1 for large text and UI boundaries), verified by measurement in both modes rather than by eye.

## Print

- One global `@media print` layer does the work. It pins dark mode back to light tokens, hides chrome and anything marked no-print, strips the main container's padding and width cap, and sets the page margin.
- Per-page print blocks are forbidden. Extend the global layer instead, or the rules fight each other.
- Mark interactive controls as non-printing and keep exactly one printable region per view. The printed sheet carries the deliverable only: no page title, no section labels, no hints, no buttons.
- Sheets size themselves to the paper. Set explicit physical dimensions for grid cells, keep each unit from splitting across pages, and force page breaks between them.
- Verify with print emulation and a screenshot before shipping any change to a printable.

## Before shipping any page change

1. The build passes.
2. The readability and contrast audit re-runs in both modes and clears the floor.
3. Zero computed italics where the project bans them, and no unexpected storage or network calls.
4. View-source shows the full content and working UI without JavaScript.
