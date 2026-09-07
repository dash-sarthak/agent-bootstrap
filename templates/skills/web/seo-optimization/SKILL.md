---
name: seo-optimization
description: Build and audit web pages that rank in Google US without tripping spam policies. Use when creating or editing any indexable page (tool pages, landing pages, content) or auditing an existing site for ranking ability. Covers Core Web Vitals, programmatic-fleet spam tripwires, structured data, canonicals, sitemaps, and AI-Overview-era strategy.
---

# SEO optimization

Apply at build time to every indexable page and as an audit before shipping. Grounded in Google's own documentation; sources at the bottom. Where Google publishes no spec, this skill says so. Never invent thresholds.

## Hard rules (these lose rankings outright)

- The tool must genuinely work and stay usable through the ads. "Misleading functionality" (a page that promises a tool but leads to ads) is a named spam policy with manual actions. Never put an ad between a control and its result. Never overlay the tool.
- No scaled template abuse. Every page needs distinct, genuinely useful value: unique data, unique guidance, real interactivity. Do not spin out dozens of near-identical variants of one tool; that trips both scaled-content abuse and doorway abuse.
- No hidden site networks. Build one strong platform with clusters under it, not many thin sites hiding the scale.
- No interstitials on entry. Banners over overlays; never redirect to a separate consent page.
- No back-button manipulation or fake controls.

## Core Web Vitals

Passing = all three at the 75th percentile of real user loads (CrUX field data), mobile and desktop measured separately. Lighthouse lab scores do not substitute (it proxies INP with TBT).

- LCP <= 2.5s. Static HTML first paint, preload the hero asset, no render-blocking chains.
- INP <= 200ms. Minimal JavaScript; the interactive tool lives in one island or lazy component; a heavy framework runtime on a static page is the usual cause of failure.
- CLS <= 0.1. Reserve space for everything that loads late: ad slots get explicit reserved heights before any ad loads, images carry width/height or aspect-ratio, fonts get fallback metrics.
- Measure in production with the `web-vitals` library and watch Search Console's CWV report.

## On-page checklist

- Self-referencing absolute canonical on every page, consistent with sitemap, links, and redirects.
- One h1 matching the search intent. Descriptive, non-exaggerated title tag. Google publishes no character limit and truncates dynamically, so ignore "60 character" folklore.
- Meta description stating what the tool does plus the qualifier that matters (free, online, no signup).
- Short hyphenated URL slug carrying the keyword.
- Internal links: every important page reachable within two clicks of home, a related-tools block on every page, visible breadcrumbs paired with BreadcrumbList JSON-LD.
- sitemap.xml with lastmod, submitted in Search Console. Useful even under 500 pages for new, underlinked sites.
- robots.txt left open to Googlebot. Blocking it blocks both Search and Google's AI surfaces.
- Images: descriptive filenames, alt text, AVIF or WebP, lazy-load below the fold only, explicit dimensions.
- HTTPS everywhere.

## Structured data

- WebApplication JSON-LD per tool: name, description, applicationCategory "UtilitiesApplication", operatingSystem "Any", offers.price "0" (USD for free tools).
- BreadcrumbList matching the visible breadcrumbs.
- Math solver markup only for step-by-step math walkthrough tools.
- Never add aggregateRating or review markup without real, visible reviews. Self-serving fabricated ratings violate structured-data policies and earn manual actions.
- Skip FAQPage markup. FAQ rich results have been restricted to authoritative government and health sites since 2023; there is no payoff for tool sites.
- Markup must match visible text. Validate with Google's Rich Results Test.

## Trust (E-E-A-T)

- Real About page with an operator identity; a method note on every calculator (formula used, data source).
- Disclose AI-assisted production where it exists. Google rewards quality regardless of production method and penalizes automation used to manipulate rankings.
- Health and finance calculators are YMYL-adjacent: cite primary sources for formulas, keep claims modest, add disclaimers.
- Each site shows one evident primary purpose, with working about, contact, and privacy pages. Google's quality bar explicitly flags content "spread across a large network of sites."

## AI-era strategy

- Assume roughly one-third CTR loss on informational queries that trigger AI Overviews (Pew: 8% vs 15% click rate; Ahrefs: position-1 CTR down ~34.5%).
- Interactive tools are structurally favored in AI-era search: Ahrefs attributes 80% of AI-search referrals to homepages, product pages, and free tools. Prefer queries where the interaction IS the answer (device tests, personal-input calculators).
- Keep real text next to the tool (how it works, the formula, a worked example). There are no extra technical requirements for AI features; crawlable, snippet-eligible content is the whole bar, and that text is what AI surfaces cite.
- AI Overview traffic folds into Search Console's Web performance type; it cannot be broken out. Watch trends, not segments.

## Never encode as specs

Google publishes nothing for: title or heading character limits, word counts, ad-density percentages, link minimums. "Excessive ads that distract from main content" is the entire published ad rule; treat any concrete number you see elsewhere as folklore.

## Ship-time audit list

1. View-source shows the complete tool UI and text without executing JavaScript.
2. Exactly one canonical, absolute, self-referencing.
3. One h1; title unique across the site.
4. JSON-LD parses and matches visible content.
5. Every ad slot has a reserved height; nothing above the fold on mobile but the tool; sticky footer capped and dismissible.
6. Page reachable from home in two internal links or fewer, present in the sitemap.
7. No interstitials or overlays on entry.
8. Passes CWV budgets on a mid-range phone profile in the lab; RUM tracking live.

## Sources

- web.dev/articles/vitals (CWV definitions, thresholds, 2024-10-31)
- developers.google.com/search/docs/essentials/spam-policies (2026-08-28)
- developers.google.com/search/docs/appearance/page-experience (2025-12-10)
- developers.google.com/search/docs/appearance/avoid-intrusive-interstitials (2025-12-10)
- developers.google.com/search/docs/appearance/structured-data/software-app (2025-12-10)
- developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls (2025-12-10)
- developers.google.com/search/docs/crawling-indexing/sitemaps/overview (2025-12-10)
- developers.google.com/search/docs/appearance/ai-features (2025-12-10)
- developers.google.com/search/docs/fundamentals/creating-helpful-content (2025-12-10)
- pewresearch.org/short-reads/2025/07/22 (AI Overview click behavior)
- ahrefs.com/blog/ai-overviews-reduce-clicks and /ai-search-traffic-by-page-type-ahrefs (secondary)
