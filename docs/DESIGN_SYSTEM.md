# LUMINALEARN AI — DESIGN SYSTEM SPECIFICATION & VISUAL HANDBOOK

> **Project Aurora | Phase 1: Product Strategy — Step 7**  
> **Document Version:** 1.0.0  
> **Classification:** Master Design System Specification & Visual Tokens Handbook (SSOT)  
> **Status:** Approved / Design Baseline  
> **Target Audience:** Design Leads, Visual Designers, Frontend Engineers, UI/UX Engineers, Accessibility Auditors  

---

## 1. Executive Summary & Design System Architecture

### 1.1 Design System Vision
The **LuminaLearn AI Design System** (*Project Aurora*) provides the comprehensive visual language, design tokens, interaction rules, component specifications, and accessibility guidelines that govern every user interface in the platform.

Inspired by the design mastery of **Apple** (clarity, depth, materials), **Notion** (content-first layout, spatial calm), **Linear** (keyboard speed, crisp micro-borders), **Stripe** (visual precision, vibrant accessible palettes), **Spotify** (fluid context transitions), **Vercel** (high-contrast monochrome elegance), and **Duolingo** (frictionless micro-delights), LuminaLearn AI balances educational clarity with an ultra-premium software experience.

```
+-----------------------------------------------------------------------------------+
|                        DESIGN SYSTEM TOKEN ARCHITECTURE                           |
|                                                                                   |
|  [BRAND IDENT & DESIGN TOKENS] ──► Color, Typography, Grid, Spacing, Shadows      |
|              │                                                                    |
|              ▼                                                                    |
|  [CORE UI COMPONENTS]          ──► Buttons, Cards, Inputs, Modals, Tables, Badges |
|              │                                                                    |
|              ▼                                                                    |
|  [PEDAGOGICAL AI COMPONENTS]   ──► LuminaTutor Bubble, Progress Rings, Hint Cards |
|              │                                                                    |
|              ▼                                                                    |
|  [UNIVERSAL ACCESSIBILITY]     ──► WCAG 2.1 AAA, Keyboard Focus, High Contrast    |
+-----------------------------------------------------------------------------------+
```

### 1.2 Core Pillars
1. **Unifying Brand Language:** Every screen, modal, button, and card looks and feels like it belongs to the same product family.
2. **Distraction-Free Focus:** High-contrast text, spacious padding, and subtle container borders eliminate visual noise, allowing students to maintain flow state.
3. **Deterministic Token System:** Design choices are codified as CSS custom properties (`var(--token)`), ensuring 100% fidelity between design specs and frontend code.
4. **Universal Inclusivity:** Native support for Dark, Light, and High-Contrast themes alongside WCAG 2.1 AAA touch target and screen reader standards.

---

## 2. Part 1: Brand Identity & Visual Language

### 2.1 Logo Philosophy & Symbolism
The LuminaLearn AI logo embodies the concept of **illumination through knowledge**. 
* **The Symbol (The Beacon Node):** An abstract, geometric icon combining an overlapping neural node network with an ascending light ray (the Aurora beam). It represents the intersection of Artificial Intelligence (nodes) and human cognitive growth (illumination).
* **The Logotype:** Set in custom-tracked, bold sans-serif typography (`LuminaLearn`) paired with a high-contrast Indigo highlight on `AI`.
* **Clear Space Rule:** Minimum margin of $1.5\times$ the symbol height around the logo mark on all surfaces.

### 2.2 Brand Personality & Visual Tone
* **Intelligent & Authoritative:** Communicates scientific rigor, academic accuracy, and enterprise trust.
* **Warm & Encouraging:** Empathetic to student frustration; celebrates small learning milestones without patronizing tone.
* **Modern & Minimal:** Eliminates 3D clutter, heavy shadows, and unnecessary gradients in favor of crisp typography, subtle glassmorphism, and clean spatial grids.

### 2.3 Illustration & Asset Style Guidelines
* **Style:** Flat vector geometry with subtle dual-tone gradient fills and semi-transparent overlay shapes. 
* **Character Representation:** Inclusive, modern, non-stereotypical vector silhouettes representing diverse global learners.
* **Forbidden Asset Styles:** Skewed 3D claymorphism, heavy cartoonish drop-shadows, overly complex multi-color realistic renderings, and non-accessible low-contrast pastel illustrations.

### 2.4 Iconography Standards (Lucide-React Specification)
* **Icon Set:** Standardized on **Lucide Icons** (`lucide-react`).
* **Stroke Weight:** Consistent 1.75px stroke width across all screen sizes (2.0px for small 16px icons).
* **Bounding Box Sizes:**
  * Small: `16px x 16px` (Inline table badges, metadata).
  * Medium: `20px x 20px` (Button icons, form inputs, nav links).
  * Large: `24px x 24px` (Section headers, card highlights).
  * Hero: `32px x 32px` (Modal headers, feature callouts).

---

## 3. Part 2: Color System & Theme Tokens

The LuminaLearn AI color system is built around an **Electric Indigo** primary core, supported by deep slate neutrals and vibrant semantic signals.

```
+-----------------------------------------------------------------------------------+
|                              COLOR PALETTE STRUCTURE                              |
|                                                                                   |
|  PRIMARY:   Electric Indigo  ──► HSL(238, 83%, 58%) [Hex: #4F46E5]                |
|  NEUTRAL:   Midnight Slate   ──► HSL(224, 71%, 4%)  [Hex: #030712]                |
|  ACCENT:    Aurora Teal      ──► HSL(172, 80%, 40%) [Hex: #0D9488]                |
|  SEMANTIC:  Success Green    ──► HSL(142, 71%, 45%) [Hex: #16A34A]                |
|             Warning Amber    ──► HSL(38, 92%, 50%)  [Hex: #F59E0B]                |
|             Destructive Red  ──► HSL(0, 84%, 60%)   [Hex: #DC2626]                |
+-----------------------------------------------------------------------------------+
```

### 3.1 Color Token Matrix

| Token Name | HSL Value | Hex Equivalent | Usage & Semantic Context |
| :--- | :--- | :--- | :--- |
| `--primary` | `hsl(238, 83%, 58%)` | `#4F46E5` | Primary CTA buttons, active tab indicators, key focus rings. |
| `--primary-hover` | `hsl(238, 83%, 50%)` | `#4338CA` | Hover state for primary interactive elements. |
| `--primary-subtle`| `hsl(238, 83%, 95%)` | `#EEF2FF` | Active row backgrounds, subtle badge fills (Light Mode). |
| `--accent-teal` | `hsl(172, 80%, 40%)` | `#0D9488` | Mastery progress rings, streak achievements, XAI insights. |
| `--success` | `hsl(142, 71%, 45%)` | `#16A34A` | Correct answer states, positive trend badges, 100% mastery. |
| `--warning` | `hsl(38, 92%, 50%)` | `#F59E0B` | At-risk student alerts, medium hesitation time warnings. |
| `--destructive` | `hsl(0, 84%, 60%)` | `#DC2626` | Incorrect attempt alerts, delete confirmation buttons, critical errors.|

### 3.2 Multi-Theme Token Mapping

```
+-----------------------------------------------------------------------------------+
|                             MULTI-THEME TOKEN MAPPING                             |
|                                                                                   |
|  TOKEN NAME              DARK THEME (DEFAULT)          LIGHT THEME                |
|  --background            hsl(224, 71%, 4%)             hsl(0, 0%, 100%)           |
|  --surface               hsl(222, 47%, 11%)            hsl(0, 0%, 98%)            |
|  --surface-subtle        hsl(217, 32%, 17%)            hsl(210, 40%, 96%)         |
|  --border                hsl(217, 32%, 17%)            hsl(214, 32%, 91%)         |
|  --foreground            hsl(213, 31%, 91%)            hsl(222, 84%, 5%)          |
|  --muted-foreground      hsl(215, 20%, 65%)            hsl(215, 16%, 47%)         |
+-----------------------------------------------------------------------------------+
```

### 3.3 High-Contrast Theme (WCAG AAA Strict Protocol)
* **Background:** Absolute Black `#000000` (Dark) / Absolute White `#FFFFFF` (Light).
* **Borders:** Crisp 2px solid borders `#FFFFFF` (Dark) / `#000000` (Light).
* **Text:** `#FFFFFF` on `#000000` achieving a maximum **21:1 contrast ratio**.

---

## 4. Part 3: Typography & Text System

LuminaLearn AI utilizes an enterprise system sans-serif font stack (**Inter**, **SF Pro**, **-apple-system**) for zero download latency and optimal screen legibility.

### 4.1 Typography Scale Specifications

| Level | Size (px / rem) | Weight | Line Height | Letter Spacing | Usage Context |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Display Hero** | `48px / 3.0rem` | 700 (Bold) | 1.1 | `-0.02em` | Landing hero title, milestone celebrations. |
| **Heading 1 (H1)**| `36px / 2.25rem`| 700 (Bold) | 1.2 | `-0.01em` | Main dashboard titles, page headers. |
| **Heading 2 (H2)**| `28px / 1.75rem`| 600 (SemiBold)| 1.25 | `-0.01em` | Major section headers, card titles. |
| **Heading 3 (H3)**| `20px / 1.25rem`| 600 (SemiBold)| 1.3 | `0.0em` | Modal titles, subsection headers. |
| **Body Large** | `18px / 1.125rem`| 400 (Regular) | 1.5 | `0.0em` | Socratic tutor chat text, main reading passages.|
| **Body Default** | `16px / 1.0rem` | 400 (Regular) | 1.5 | `0.0em` | Standard UI labels, inputs, table content. |
| **Body Small** | `14px / 0.875rem`| 400 (Regular) | 1.4 | `0.01em` | Table secondary text, form helper text. |
| **Caption / Badge**| `12px / 0.75rem`| 600 (SemiBold)| 1.4 | `0.02em` | Metadata tags, status badges, timestamps. |
| **Code / Math** | `15px / 0.937rem`| 400 (Mono) | 1.4 | `0.0em` | LaTeX math equations, code blocks. |

---

## 5. Part 4: Layout & Spacing System

### 5.1 Spatial 8px Grid System
All margins, padding, container heights, and component gaps MUST be calculated in multiples of **8px** (4px permitted for micro-alignment).

$$\text{Spacing Tokens: } 4\text{px} \, (0.5), \, 8\text{px} \, (1), \, 16\text{px} \, (2), \, 24\text{px} \, (3), \, 32\text{px} \, (4), \, 48\text{px} \, (6), \, 64\text{px} \, (8)$$

```
+-----------------------------------------------------------------------------------+
|                                SPATIAL GRID SCALE                                 |
|                                                                                   |
|  [4px]  ──► Micro-padding inside badges and icon align                            |
|  [8px]  ──► Gap between inline buttons, label-to-input margin                     |
|  [16px] ──► Standard card internal padding, list item gap                         |
|  [24px] ──► Section spacing inside cards, modal body padding                      |
|  [32px] ──► Grid gap between dashboard cards                                      |
|  [48px] ──► Page header to content margin                                         |
|  [64px] ──► Major page section separation                                         |
+-----------------------------------------------------------------------------------+
```

### 5.2 Responsive Breakpoints & Containers

| Breakpoint Name | Min Width | Max Container Width | Margins (Gutter) | Columns | Target Devices |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Mobile (sm)** | `320px` | `100%` | 16px | 4 | Smartphones (iPhone, Android). |
| **Tablet (md)** | `768px` | `720px` | 24px | 8 | iPads, Tablets, Portrait Laptops. |
| **Desktop (lg)** | `1024px` | `960px` | 32px | 12 | Standard Laptops, MacBooks. |
| **Desktop XL (xl)**| `1280px` | `1200px` | 32px | 12 | Large Desktop Monitors. |
| **Ultra-Wide (2xl)**| `1536px` | `1400px` | 48px | 12 | 4K & Ultra-wide Workstations. |

---

## 6. Part 5: Component Design Language Specifications

This section defines the precise visual design contracts for core UI components.

---

### 6.1 Button Component Specifications

```
+-----------------------------------------------------------------------------------+
|                               BUTTON DESIGN VARIANTS                              |
|                                                                                   |
|  [PRIMARY]    ──► Solid Electric Indigo Fill, White Text, Subtle Hover Glow       |
|  [SECONDARY]  ──► Surface Fill, Subtle Border, Contrast Foreground Text           |
|  [OUTLINE]    ──► Transparent Fill, 1px Border, Background Text                   |
|  [GHOST]      ──► Transparent Fill, No Border, Hover Background Highlight         |
|  [GLASS]      ──► Backdrop Blur 12px, 70% Opacity Surface Fill, Micro Border     |
+-----------------------------------------------------------------------------------+
```

* **Height Specs:** Small (`32px`), Default (`40px`), Large (`48px`).
* **Border Radius:** Standard `--radius` (`0.75rem / 12px`).
* **Focus State:** 2px ring in primary color with 2px offset (`ring-2 ring-primary ring-offset-2`).
* **Disabled State:** Opacity 50%, pointer events disabled (`cursor: not-allowed`).

---

### 6.2 Card Surface Component Specifications
* **Base Surface:** Layer 1 surface fill (`--surface`) with 1px border (`--border`).
* **Glass Variant:** Backdrop filter `blur(12px)` with 70% surface opacity and subtle top-edge highlight border (`rgba(255, 255, 255, 0.1)`).
* **Hover Interaction:** Subtle vertical elevation lift (`translateY(-2px)`) with shadow transition over 200ms.

---

### 6.3 Input Fields & Form Controls
* **Height:** `40px` for standard inputs.
* **States:** Default (1px border), Focus (2px primary ring), Valid (Green right-icon checkmark), Error (Red 1px border + red helper text below).
* **Accessibility:** Label MUST be permanently bound via `htmlFor` matching input `id`.

---

### 6.4 Skeleton Screens & Loading Indicators
* **Skeleton Shimmer:** Smooth linear gradient animation (`bg-gradient-to-r from-surface-subtle via-border to-surface-subtle`) sweeping over 1.5 seconds.
* **Spinner Indicator:** Dual-ring CSS spinner utilizing `--primary` for active arc and `--border` for track.

---

## 7. Part 6: Specialized AI & Pedagogical Components

```
+-----------------------------------------------------------------------------------+
|                        SPECIALIZED PEDAGOGICAL COMPONENTS                         |
|                                                                                   |
|  1. LUMINATUTOR BUBBLE  ──► Floating AI Avatar with active pulse indicator      |
|  2. RECOMMENDATION CARD ──► ZPD concept callout with 1-click "Start" CTA          |
|  3. LEARNING INSIGHT CARD──► XAI explanation detailing *why* topic was prescribed |
|  4. PROGRESS RING       ──► Circular SVG progress ring with gradient stroke       |
|  5. STUDY STREAK BADGE  ──► Flame icon with animated count indicator              |
|  6. HINT SCAFFOLD CARD  ──► Collapsible progressive hint container                |
+-----------------------------------------------------------------------------------+
```

### 7.1 SCR-COMP-01: LuminaTutor Floating Bubble
* **Visual Spec:** Circular 48px floating action button anchored to bottom-right viewport ($24\text{px}$ offset).
* **Styling:** Electric Indigo background with subtle glowing aura (`box-shadow: 0 0 20px rgba(99, 102, 241, 0.4)`).
* **Micro-Interaction:** Hover expands button slightly (scale 1.05) to reveal label *"Ask LuminaTutor"*.

### 7.2 SCR-COMP-02: Progress Ring (SVG Component)
* **Visual Spec:** Circular SVG with track thickness of 8px.
* **Gradient Fill:** Gradient transition from Aurora Teal (`#0D9488`) to Electric Indigo (`#4F46E5`).
* **Center Label:** Displays percentage complete (`75%`) in bold H3 typography.

### 7.3 SCR-COMP-03: Socratic Hint Scaffold Card
* **Visual Spec:** Card container with 4 collapsible hint accordions.
* **Stage Markers:** Stage 1 (Conceptual Hint), Stage 2 (Visual Analogy), Stage 3 (Worked Similar Example), Stage 4 (Step-by-Step Breakdown).
* **Unlock Interaction:** Stages unlock progressively as student requests additional help.

---

## 8. Part 7: Interaction Design & Micro-Animations

### 8.1 Transition & Timing Guidelines

$$\text{Standard Duration: } 150\text{ms} \le t \le 200\text{ms} \quad | \quad \text{Easing Curve: } \text{cubic-bezier}(0.16, 1, 0.3, 1)$$

```
+-----------------------------------------------------------------------------------+
|                           MICRO-ANIMATION SPECIFICATIONS                          |
|                                                                                   |
|  BUTTON HOVER:   150ms ease-out | Background color shift + scale 1.01           |
|  BUTTON PRESS:   100ms ease-in  | Scale down to 0.98                            |
|  MODAL ENTER:    200ms ease-out | Fade-in + scale up from 0.95 to 1.0           |
|  TOAST NOTIFY:   200ms ease-out | Slide-in from top-right + fade-in             |
|  CARD ELEVATION: 200ms ease-out | translateY(-2px) + shadow expand                |
+-----------------------------------------------------------------------------------+
```

---

## 9. Part 8: Accessibility & Universal Design (WCAG 2.1 AAA)

### 9.1 Touch Target Rules
All interactive controls (buttons, links, form toggles, checkbox areas) MUST maintain a minimum touch target size of **$44\text{px} \times 44\text{px}$** on mobile viewports.

### 9.2 Reduced Motion Protocol
When `prefers-reduced-motion: reduce` is detected in user system settings:
* All CSS animations and scale transitions are set to `duration-0`.
* Modal fade-ins occur instantly without scale transformation.
* Skeleton shimmer animations are replaced with static muted backgrounds.

---

## 10. Part 9: Responsive Layout Design

```
+-----------------------------------------------------------------------------------+
|                        RESPONSIVE LAYOUT ADAPTATION RULES                         |
|                                                                                   |
|  DESKTOP (>=1024px): ──► Fixed 240px Sidebar + Multi-Column Card Grid             |
|  TABLET (768px-1023px):► Collapsible Drawer Sidebar + 2-Column Responsive Grid     |
|  MOBILE (<768px):    ──► Bottom Navigation Bar + 1-Column Stacked Cards           |
+-----------------------------------------------------------------------------------+
```

---

## 11. Part 10: Engineering Handoff Token Specifications

Frontend engineers can implement this design system directly using the following CSS custom property specification file (`src/styles/tokens.css`):

```css
:root {
  /* Color Tokens */
  --primary: hsl(238, 83%, 58%);
  --primary-hover: hsl(238, 83%, 50%);
  --primary-subtle: hsl(238, 83%, 95%);
  --accent-teal: hsl(172, 80%, 40%);
  --success: hsl(142, 71%, 45%);
  --warning: hsl(38, 92%, 50%);
  --destructive: hsl(0, 84%, 60%);

  /* Spatial Grid Tokens */
  --space-05: 0.25rem; /* 4px */
  --space-1: 0.5rem;   /* 8px */
  --space-2: 1.0rem;   /* 16px */
  --space-3: 1.5rem;   /* 24px */
  --space-4: 2.0rem;   /* 32px */
  --space-6: 3.0rem;   /* 48px */
  --space-8: 4.0rem;   /* 64px */

  /* Radius Tokens */
  --radius-sm: 0.375rem; /* 6px */
  --radius-md: 0.5rem;   /* 8px */
  --radius-lg: 0.75rem;  /* 12px */
  --radius-full: 9999px;

  /* Elevation Shadows */
  --shadow-subtle: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
  --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
}
```

---
