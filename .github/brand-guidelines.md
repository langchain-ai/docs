# LangChain Brand Guidelines

Full brand color palette, typography, and visual identity reference. For the condensed mermaid diagram palette, see the "Mermaid diagram styling" section in `CLAUDE.md` / `AGENTS.md`.

## Colors

### Primary Brand Palette — Dark Blue Family

- Dark Blue: `#030710` — Primary dark background, replaces pure black in light mode
- Dark Shade 1: `#0D1322` — Secondary dark background (darkmode UI)
- Dark Shade 2: `#161F34` — Accent dark background
- Dark Shade 3: `#2F4B68` — Dark accent
- Dark Shade 4: `#40668D` — Mid-dark accent
- Blue: `#006DDD` — Core brand blue, used in gradients and accents

### Primary Brand Palette — Light Blue Family

- Light Blue: `#7FC8FF` — Primary light accent, logomark on dark backgrounds
- Light Tint 1: `#99D3FF`
- Light Tint 2: `#B2DEFF`
- Light Tint 3: `#CCE9FF`
- Light Tint 4: `#E5F4FF`
- Light Tint 5: `#F2FAFF` — Replaces pure white in light mode UI

### Extended Product Palette

- Plum: `#885270` (deep: `#441E33`, light: `#C78EAD`, lighter: `#EBD0F0`)
- Purple: `#504B5F` (mid: `#7E65AE`, light: `#D5C3F7`, lighter: `#FDF3FF`)
- Peach: `#634643` (mid: `#FBB0A5`, light: `#B27D75`, lighter: `#F8E8E6`) — deepest shade reserved for warning states only
- Green: `#6E8900` (deep: `#2E3900`, light: `#E3FF8F`, lighter: `#F6FFDB`)

### Gradients (only these three are permitted)

- Dark Blue to Blue: `#030710` to `#006DDD`
- Dark Blue to Light Blue: `#030710` to `#7FC8FF`
- Blue to Light Blue: `#006DDD` to `#7FC8FF`

### Color rules

- Do not create new colors outside the palette
- Do not overlay colors
- In darkmode: use Dark Blue / Dark Shade 1 as backgrounds, lighter tints for text and accents
- In lightmode: use Dark Blue (`#030710`) instead of pure black, Light Tint 5 (`#F2FAFF`) instead of pure white
- Never use pure black (`#000000`) or pure white (`#FFFFFF`)

## Typography

**Primary Typeface: Lausanne** (fallback: Inter)

- Weights: 600 Bold, 400 Medium, 250 Regular
- 600 Bold should be used sparingly — headlines are typically set in 250 Regular

**Secondary Typeface: Aeonik Mono** (fallback: IBM Plex Mono)

- Used for product names (lowercase), code, short body copy, CTAs, and H2 headings

## Brand architecture

- **LangChain** — Parent brand
- **LangSmith** — Sub-brand / Platform (services: Observability, Evaluation, Deployment, Fleet)
- **LangGraph** — Open source framework
- **Deep Agents** — Open source framework

## CSS variables (dark mode default)

```css
--bg-primary: #030710;
--bg-secondary: #0D1322;
--bg-card: #161F34;
--text-primary: #F2FAFF;
--text-secondary: #99D3FF;
--accent: #7FC8FF;
--accent-bright: #006DDD;
```

## CSS variables (light mode)

```css
--bg-primary: #F2FAFF;
--bg-secondary: #E5F4FF;
--bg-card: #CCE9FF;
--text-primary: #030710;
--text-secondary: #161F34;
--accent: #7FC8FF;
--accent-bright: #006DDD;
```
