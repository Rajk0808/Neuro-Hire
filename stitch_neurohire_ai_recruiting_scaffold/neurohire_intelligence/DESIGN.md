---
name: NeuroHire Intelligence
colors:
  surface: '#13131b'
  surface-dim: '#13131b'
  surface-bright: '#393841'
  surface-container-lowest: '#0d0d15'
  surface-container-low: '#1b1b23'
  surface-container: '#1f1f27'
  surface-container-high: '#292932'
  surface-container-highest: '#34343d'
  on-surface: '#e4e1ed'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e4e1ed'
  inverse-on-surface: '#303038'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#c3c0ff'
  on-secondary: '#1d00a5'
  secondary-container: '#3626ce'
  on-secondary-container: '#b3b1ff'
  tertiary: '#ffb783'
  on-tertiary: '#4f2500'
  tertiary-container: '#d97721'
  on-tertiary-container: '#452000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#e2dfff'
  secondary-fixed-dim: '#c3c0ff'
  on-secondary-fixed: '#0f0069'
  on-secondary-fixed-variant: '#3323cc'
  tertiary-fixed: '#ffdcc5'
  tertiary-fixed-dim: '#ffb783'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#703700'
  background: '#13131b'
  on-background: '#e4e1ed'
  surface-variant: '#34343d'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-page: 40px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The design system for this platform prioritizes **Executive Intelligence** and **Autonomous Flow**. It is built for a high-stakes recruiting environment where AI agents and human recruiters collaborate. The aesthetic is "Premium Data-Dense," balancing a high volume of information with a sophisticated, uncluttered interface.

The style is **Corporate / Modern** with a lean toward **Minimalism**. It avoids unnecessary decorative elements like gradients or heavy shadows in favor of crisp lines, purposeful motion, and a layout that emphasizes "Multi-Agent Status Visibility." The UI should feel like a high-performance command center: authoritative, calm, and hyper-efficient.

## Colors
The palette is rooted in a professional **Slate** foundation, optimized for deep-focus "Dark Mode" as the primary experience. 

- **Primary Indigo (#6366f1):** Used for primary actions, active AI status indicators, and focus states.
- **Deep Indigo (#4f46e5):** Used for hover states on primary elements.
- **Surface Palette:** In dark mode, use Slate-900 (#0f172a) for the background and Slate-800 (#1e293b) for elevated surfaces. 
- **Functional UI:** No gradients are permitted on buttons, inputs, or headers to ensure maximum legibility and a sober, technical feel.

## Typography
The system uses **Inter** exclusively to maintain a utilitarian, technical clarity. 

- **Headings:** Set at Weight 500 (Medium) to provide clear hierarchy without the visual "heaviness" of a bold weight. This maintains the sleek, premium feel.
- **Body:** Set at Weight 400 (Regular). 
- **Data Tables:** For the dense talent intelligence views, use `body-sm` to maximize information density while maintaining a comfortable line-height for readability.
- **Labels:** Use `label-md` for small metadata, AI tags, and table headers.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. Navigation and sidebars are fixed, while the main content area is fluid with a maximum width of 1600px to prevent excessive line lengths in data-heavy views.

- **Grid:** 12-column system with 24px gutters.
- **Agent Panels:** Use a right-aligned persistent drawer for AI agent status updates, allowing users to monitor autonomous tasks while managing the candidate pipeline.
- **Breakpoints:**
  - **Mobile (<768px):** Single column, 16px page margins, hidden sidebars (accessible via hamburger).
  - **Tablet (768px - 1024px):** Condensed sidebars, 24px margins.
  - **Desktop (>1024px):** Full multi-panel view, 40px page margins.

## Elevation & Depth
This design system uses **Tonal Layers** and **Low-Contrast Outlines** rather than dramatic shadows.

- **Surfaces:** Use 1px borders (#1e293b in dark mode / #e2e8f0 in light mode) to define element boundaries. 
- **Depth:** Higher elevation is communicated by shifting the background color slightly lighter (e.g., a card sitting on the background shifts from Slate-950 to Slate-900).
- **Shadows:** Use a singular, highly-diffused `shadow-sm` for cards to provide just enough lift to separate the content from the base layer.
- **Motion:** All new views enter with a staggered **fade + 16px slide-up** transition. This reinforces the "fluid" feel of the platform.

## Shapes
The shape language is refined and professional. 

- **Rounded-XL (1rem / 16px):** Used for primary containers, dashboard cards, and modal windows.
- **Rounded-MD (0.5rem / 8px):** Used for buttons, input fields, and smaller nested components.
- **Pill:** Reserved exclusively for status indicators (e.g., "AI Sourcing," "Interviewing") and selection chips.

## Components
- **Buttons:** Solid Indigo-500 for primary actions. No gradients. Ghost buttons with 1px slate borders for secondary actions.
- **Cards:** Background Slate-900 (Dark) or White (Light), 1px border, 16px corner radius. Padding should be a generous 24px.
- **AI Status Chips:** Use a subtle pulse animation on the leading icon (Lucide "Sparkles" or "Cpu") to indicate active autonomous processing.
- **Input Fields:** 1px border, Slate-800 background in dark mode. Focus state should use a 2px Indigo-500 ring.
- **Lists:** Clean rows with 1px bottom borders. Hover states should trigger a subtle background shift to Slate-800/50.
- **Icons:** Use **Lucide React** icons. Set stroke width to 1.5px for a light, modern appearance that complements the Inter typeface.
- **Multi-Agent HUD:** A specialized component showing a stack of active AI "thoughts" or processes, using monospaced micro-copy for a technical edge.