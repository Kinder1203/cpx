# Design Reference Intake

This file is the intake gate for external UI references, Figma Community files, and
design-system seeds. Do not treat a downloaded community file as source of truth until
this checklist is filled and reviewed.

## Decision Status

- Current status: no external Figma file selected.
- Default source of truth: `docs/app/design.md`, `docs/app/wireframes.md`, and
  `docs/app/visual_quality_bar.md`.
- Preferred adoption level: visual and component reference first, direct import only after
  license and security review.
- MCP stance: use official Figma MCP only when a specific Figma file URL exists and the
  optional app UI profile is intentionally enabled.

## Candidate Record

Use one record per candidate.

```yaml
name:
source_url:
source_type: figma_community | official_system | open_source_repo | screenshot_reference | other
author_or_maintainer:
license:
license_checked: false
last_reviewed:
adoption_decision: reject | reference_only | token_seed | component_seed | direct_adapt
reason:
```

## Fit Checklist

- Product fit: supports a working CPX cockpit, not a marketing landing page.
- Density fit: handles forms, chat/transcript, status panels, tables, tabs, modals, and
  evaluation summaries without oversized cards.
- Medical education fit: feels clinical and instructional without implying diagnosis,
  treatment, hospital production use, or real patient data handling.
- Responsive fit: includes mobile layouts where input remains reachable and content does
  not overlap.
- Accessibility fit: has clear contrast, focus states, keyboard-reachable controls, and
  non-color-only state indicators.
- Token fit: color, spacing, typography, radius, elevation, and state tokens can map to
  `docs/app/design.md` without rewriting the product structure.
- Component fit: includes practical states for loading, empty, error, disabled, selected,
  hover, focus, and validation feedback.
- Anti-AI fit: avoids generic AI dashboard tropes, stock medical gradients, glassmorphism,
  decorative glow, bokeh/orb backgrounds, and one-note blue/cyan palettes.
- Security fit: no unreviewed runtime package, plugin code, external script, tracking asset,
  or copied secret is required to use it as a reference.

## Reference Priorities

Prefer references with:

- Dense operational app surfaces over portfolio, landing, or hero templates.
- Mature component behavior over decorative visual novelty.
- Neutral clinical usability over futuristic AI/medical styling.
- Clear state design over static screenshot-only polish.
- Evidence of maintenance, license clarity, and community review.

Avoid references that:

- Make the first viewport a generic hero instead of the usable CPX session.
- Depend on large decorative illustrations to look complete.
- Use large rounded cards for every section.
- Hide core task controls behind hover-only or animation-only interactions.
- Require paid assets, unclear licenses, or untrusted plugins for the demo.

## Adoption Output

When a candidate is accepted, record:

- Which tokens are adopted.
- Which components are adopted.
- Which patterns are explicitly rejected.
- What still needs manual design judgment.
- What screenshots must be captured during QA.
