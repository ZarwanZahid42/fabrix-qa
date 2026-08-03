# FabriX-QA — UI/UX Design Direction

> **Version:** 1.0 — Initial Scaffold  
> **Last Updated:** 2026-08-04

---

## 1. Design Philosophy

FabriX-QA lives on a production floor monitor and is used by workers in bright, noisy environments. The design must:

1. **Be instantly readable** — high contrast, large text, clear status indicators
2. **Communicate urgency** — critical defects must visually demand attention
3. **Feel premium and modern** — the system is a showpiece FYP; it should impress evaluators
4. **Minimize cognitive load** — operators should understand the system state in under 3 seconds

---

## 2. Color Palette

### Primary Palette
| Token | Hex | Usage |
|---|---|---|
| `brand-900` | `#0A0A14` | Page background |
| `brand-800` | `#0F0F23` | Card / panel background |
| `brand-700` | `#161630` | Elevated surfaces |
| `brand-600` | `#1E1E40` | Input backgrounds, borders |
| `brand-500` | `#2A2A5A` | Hover states, dividers |
| `brand-accent` | `#00D4FF` | Primary actions, highlights, links |
| `brand-accent-dim` | `#0099BB` | Accent hover states |

### Semantic Colors
| Token | Hex | Usage |
|---|---|---|
| `brand-success` | `#00E096` | Grade A, normal status, success states |
| `brand-warning` | `#FFB800` | Grade B/C, warnings, medium severity |
| `brand-danger` | `#FF4D6D` | Grade D, critical defects, errors |
| White | `#FFFFFF` | Primary text on dark backgrounds |
| `gray-400` | `#9CA3AF` | Secondary/muted text |

### Grade Color Mapping
| Grade | Color | Meaning |
|---|---|---|
| **A** | `#00E096` (green) | Excellent — ship as-is |
| **B** | `#FFB800` (amber) | Good — minor defects |
| **C** | `#FF8C42` (orange) | Acceptable — review before shipment |
| **D** | `#FF4D6D` (red) | Reject — do not ship |

---

## 3. Typography

| Element | Font | Weight | Size |
|---|---|---|---|
| Page title | Inter | 700 (Bold) | 28px |
| Section heading | Inter | 600 (SemiBold) | 20px |
| Card title | Inter | 600 (SemiBold) | 16px |
| Body text | Inter | 400 (Regular) | 14px |
| Muted/secondary | Inter | 400 (Regular) | 12px |
| Monospace data | JetBrains Mono | 400 | 13px |
| Grade badge | Inter | 800 (ExtraBold) | 32px |
| Alert severity label | Inter | 700 (Bold) | 12px (uppercase) |

---

## 4. Dashboard Layout

### 4.1 Shell Structure
```
┌──────────┬────────────────────────────────────────────────┐
│          │  TOP BAR: Logo | Line selector | User menu     │
│ SIDEBAR  ├────────────────────────────────────────────────┤
│          │                                                │
│ Overview │              PAGE CONTENT                      │
│ Reports  │                                                │
│ Alerts   │                                                │
│ Settings │                                                │
│          │                                                │
│ [Logout] │                                                │
└──────────┴────────────────────────────────────────────────┘
```
- Sidebar: 240px wide, dark (`brand-800`), icons + labels
- Topbar: 64px tall, slightly lighter (`brand-700`)
- Content area: scrollable, padded 24px

### 4.2 Overview Page Layout
```
┌─────────────────────────────────────────────────────────┐
│  GRADE CARD (current)   │  DEFECT COUNT  │  YIELD LOSS  │
│  [A]  Excellent         │  [12 defects]  │  [2.3%]      │
├─────────────────────────┴────────────────┴──────────────┤
│                                                         │
│  LIVE DEFECT FEED (WebSocket)        │  CAMERA PREVIEW  │
│  [timestamp] [type] [severity] [ack] │  [frame + ROI]   │
│  [timestamp] [type] [severity] [ack] │                  │
│  ...                                 │                  │
├──────────────────────────────────────┴──────────────────┤
│  GRADE TREND (Recharts line chart — last 20 rolls)      │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Component Design Tokens

#### Cards
- Background: `brand-800`
- Border: `1px solid rgba(255,255,255,0.08)`
- Border radius: `12px`
- Padding: `20px 24px`
- Box shadow: `0 4px 24px rgba(0,0,0,0.4)`
- Hover: lift effect with `translateY(-2px)` + shadow increase

#### Status Badges
- Pill shape, uppercase text, 11px font
- Grade A: green background + dark text
- Grade D / Critical: pulsing animation (`animate-pulse`)

#### Alert Rows
- Critical: left border 4px `brand-danger` + subtle red tint background
- Medium: left border 4px `brand-warning`
- Low: left border 4px `brand-accent-dim`

---

## 5. Animations & Interactions

| Interaction | Animation |
|---|---|
| Page transition | Fade in (200ms ease-out) |
| Card hover | `translateY(-2px)` + shadow (150ms ease) |
| New defect in live feed | Slide-in from right (300ms ease-out) |
| Grade badge (Grade D) | Pulse animation (1s infinite) |
| Alert acknowledge | Fade out + collapse (200ms) |
| Button click | Scale down (0.97) + release (100ms) |
| Sidebar item active | Left border accent highlight + bg tint |

---

## 6. Responsive Design

The dashboard is designed primarily for **1920×1080** and **1440×900** desktop monitors.
Minimum supported viewport: **1280px wide** (no mobile support in v1.0).

---

## 7. Accessibility

- All interactive elements have `:focus-visible` ring styles
- Color is never the sole differentiator — always include text label or icon
- WCAG AA contrast minimum on all text elements
- Semantic HTML: `<nav>`, `<main>`, `<section>`, `<article>` used correctly
