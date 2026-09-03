# FabriX-QA Website Design Specification

**Version:** 1.0 design baseline
**State:** Direction approved; UI not implemented
**Last updated:** 2026-08-29
**Platform:** Website only, optimized for factory desktops and wall/line monitors

## 1. Experience principles

1. **State in three seconds:** an operator should identify line status, current roll grade, new critical defects, and connection health at a glance.
2. **Evidence before decoration:** defect crop, heatmap, confidence, score contribution, timestamp, and source context stay close together.
3. **Urgency without alarm fatigue:** reserve strong motion/red for actionable critical states; use acknowledgement, cooldown, and clear ownership.
4. **Role relevance:** each role sees the decisions it can make, while backend RBAC remains authoritative.
5. **Honest uncertainty:** confidence, anomaly state, stale data, unavailable media, and manual corrections are visible.
6. **Factory resilient:** high contrast, large click targets, keyboard operation, and layouts that remain legible on 1280px+ screens.

## 2. Information architecture

| Area | Operator | Maintenance | Manager |
|---|---|---|---|
| Live overview | Primary | Primary | Summary |
| Defect detail/heatmap | View and acknowledge | Diagnose | Review |
| Line/roll history | Recent/assigned | Technical trends | Full history |
| Alerts | Assigned and actionable | Technical alerts | Policy and delivery oversight |
| Reports/yield | Limited operational summary | Quality/line trends | Full reports and export |
| Configuration | None or tightly limited | Permitted camera/line settings | Quality/alert policy |
| Users and roles | No | No | Authorized administration |

Proposed routes are `/login`, `/overview`, `/rolls`, `/rolls/[id]`, `/alerts`, `/reports`, and role-gated `/settings`. Route names remain provisional until Phase 1 workflow validation.

## 3. Dashboard hierarchy

```text
Top bar: FabriX-QA | line selector | connection/data freshness | user menu
Sidebar: Overview | Rolls | Alerts | Reports | role-permitted Settings
Main:
  Status strip: active roll | four-point score | A/B/C/D | yield loss | inspected length
  Primary left: live defect feed
  Primary right: selected defect crop + heatmap + evidence
  Secondary: defect rate/type and grade trend charts
  Footer/status: camera | AI model | backend | database | last update
```

A critical alert may use a persistent banner, but it must not cover live evidence or trap keyboard focus.

## 4. Visual language

The direction is dark industrial instrumentation: deep navy surfaces, cool cyan for normal interactivity, and restrained semantic colors.

| Token | Value | Use |
|---|---|---|
| `canvas` | `#080C14` | Main background |
| `surface` | `#101827` | Cards and navigation |
| `surface-raised` | `#182235` | Selected/elevated content |
| `border` | `#2A3850` | Dividers and controls |
| `text-primary` | `#F7FAFC` | Primary content |
| `text-muted` | `#A9B7CB` | Secondary content |
| `accent` | `#27C2E8` | Focus, actions, active navigation |
| `success` | `#22C55E` | Healthy state / Grade A candidate |
| `warning` | `#F5B942` | Attention / Grade B-C context |
| `danger` | `#F05252` | Critical / Grade D context |
| `info` | `#60A5FA` | Neutral system information |

Grade colors always include the letter and label; severity always includes text/icon. Color is never the only signal. Final tokens must be contrast-tested before implementation.

Typography: a readable sans-serif for UI and a tabular/monospace treatment for measurements, timestamps, confidence, and score values. Minimum default body size is 16px on operations views. Use tabular numerals to prevent metric cards from visually jumping.

## 5. Core components and states

### Live defect row

Show capture time, defect type, severity, confidence, four-point contribution, line/roll, acknowledgement, and media availability. A new item may briefly highlight; do not use continuous animation.

### Heatmap viewer

Show original/ROI crop and overlay with a visible legend/opacity control. Preserve aspect ratio and make the bounding region clear. Include model/version and explain that the heatmap is supporting evidence, not proof of causality. Provide accessible text describing defect label, location, confidence, and anomaly status.

### Grade and score card

Keep these separate:

- normalized four-point score with units and inspected coverage;
- A/B/C/D grade with rule-set version;
- yield-loss estimate with formula/version and uncertainty/assumptions;
- manual correction badge and reason when present.

### Connection and freshness

Every live surface supports: connecting, live, reconnecting, stale, disconnected, paused, and error. Show last successful event time and avoid displaying stale metrics as current.

### Empty/loading/error

Use skeletons only while a response is genuinely pending. Empty states explain why no data exists and the next valid action. Errors offer retry/recovery guidance without exposing internal details.

## 6. Charts and reports

Recharts is used for:

- defect rate over inspected length/time;
- defect-type distribution;
- four-point score and grade trend by roll;
- yield-loss trend;
- alert count and acknowledgement time.

Every chart needs title, date/roll range, units, legend, accessible summary, meaningful tooltip, and honest handling of missing intervals. Do not plot A/B/C/D as an unexplained numeric line; use categorical bands or clearly documented mapping. Avoid 3D charts, decorative gradients that distort values, dual axes without strong need, and truncated axes that exaggerate changes.

Reports use print-friendly light surfaces even if the dashboard is dark. Exported data states timezone, units, filters, model/rule version, and generation time.

## 7. Interaction and motion

- Keyboard-visible focus for all interactive elements.
- Minimum target size of 44×44 CSS pixels for primary factory controls.
- Motion duration generally 120–220ms and disabled/reduced under `prefers-reduced-motion`.
- New-event highlighting is brief; critical pulsing is avoided because it creates fatigue.
- Destructive or policy-changing actions require clear labels and appropriate confirmation.
- Grade corrections require a reason and preview of audit impact.
- WebSocket reconnection uses unobtrusive status with escalation only when data becomes stale.

## 8. Layout and browser support

Primary evaluation viewports are 1920×1080, 1440×900, and 1280×720. Below the supported operational width, panels may stack for browser usability, but no mobile app/navigation mode will be designed. Validate current Chromium, Firefox, and Edge desktop browsers used in the evaluation environment.

## 9. Accessibility and usability acceptance

- Target WCAG 2.2 AA for contrast, focus, keyboard, semantics, names, and error identification.
- Use landmarks, meaningful heading order, real buttons/links, labelled forms, and live regions only for important changes.
- Do not announce every defect event to screen readers; provide a controlled summary and critical-alert channel.
- Preserve zoom to 200% for core workflows without hidden actions.
- Test common color-vision deficiencies and bright-room readability.
- Conduct task-based walkthroughs with proxies for all three roles during Phase 1 and Phase 4.

## 10. Design deliverables still required

- Validated user journeys and permission matrix.
- Low-fidelity wireframes for all core routes and states.
- Component inventory and final Tailwind design tokens.
- Heatmap viewer behavior and evidence wording.
- Alert severity/cooldown/escalation presentation.
- Report templates and print/export specification.
- Accessibility and usability test scripts.
