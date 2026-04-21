# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev       # Start local dev server (hot reload)
npm run build     # Build static site to dist/
npm run preview   # Preview the production build locally
```

No lint, format, or test scripts are configured.

## Architecture

This is a static personal website (portfolio + research) for a mathematics teacher, built with **Astro 4** and deployed as a fully static site.

### Multilingual routing

The site supports three languages via Astro's native i18n. Spanish is the default and has no URL prefix; Catalan uses `/ca/`, English uses `/en/`. This is set in `astro.config.mjs` with `prefixDefaultLocale: false`.

- Translation strings live in `src/i18n/ui.ts` as a plain dictionary. Each page calls `getLangFromUrl()` and `useTranslations()` to get the right strings.
- Each language has its own page files under `src/pages/`, `src/pages/ca/`, and `src/pages/en/`. There is no single dynamic `[lang]` page — each locale is a separate `.astro` file.

### Page / layout / component flow

```
src/pages/*.astro  →  BaseLayout.astro  →  Nav.astro + Footer.astro
```

`BaseLayout` (`src/layouts/BaseLayout.astro`) wraps every page and is responsible for:
- HTML boilerplate, meta tags, and the `lang` attribute on `<html>`
- Loading KaTeX via CDN for math rendering
- A blocking inline script that reads `localStorage` to set `data-theme` before paint (prevents flash)

`Nav.astro` renders the sticky header with the language switcher and light/dark theme toggle. Active link highlighting reads `Astro.url.pathname`.

### Math rendering

KaTeX is loaded from CDN in `BaseLayout` and auto-renders inline (`$...$`) and display (`$$...$$`) math at runtime. Research pages are math-heavy — LaTeX in content must be valid KaTeX syntax.

### Styling

- Global tokens and resets are in `src/styles/global.css` using CSS custom properties (`--text`, `--bg`, `--accent`, etc.) on `html[data-theme]`.
- Component styles are scoped inside each `.astro` file with `<style>`.
- BEM naming is used: `.card__title`, `.hero__photo-frame`, `.nav__brand`.
- Sass is available as a dependency but styles are currently plain CSS.

### No client-side JS framework

There is no React, Vue, or Svelte. All interactivity (theme toggle) is plain inline scripts. Astro components do not use `client:*` directives — the site is fully server-rendered at build time.
