# Pixel Asset Pipeline

This document defines the asset contract for the 2D pixel CPX serious simulation. It does
not require final art assets before the hackathon. It prevents generated art, sprite sheets,
and app code from drifting into incompatible formats.

## Decision Status

- Status: pipeline contract selected, assets not yet produced.
- Default implementation: sprite sheets with metadata, animated with CSS `steps()` first.
- Source files: Aseprite, Pixelorama, Piskel, or curated PNG frames are all acceptable if
  exported into the same runtime contract.
- Heavy engine status: not default.

## Goals

- Make the encounter feel like a serious game without copying Rhythm Doctor, Pokemon,
  Duolingo, or protected assets.
- Keep UI controls clinically readable while the encounter scene uses pixel art.
- Support fast AI-assisted asset generation while preserving manual curation, provenance,
  and consistent visual style.
- Keep patient state visually clear for screenshots and live demo.

## Minimum Asset Set

For the first playable demo, produce only:

- One patient sprite:
  - `idle`
  - `discomfort`
  - `critical`
- One learner or clinician back-view sprite:
  - `idle`
  - `ask`
  - `think`
- One encounter background.
- Small UI effects:
  - selected question
  - stability decrease
  - risk flag
  - mission clear
  - critical safety event

Avoid producing many disease-specific characters before the day-of topic is known.

## Repository Layout

Recommended layout once assets exist:

```text
assets/
  pixel/
    README.md
    source/
      patient_001.aseprite
      clinician_back.aseprite
      clinic_room.aseprite
    frames/
      patient_001_idle_00.png
      patient_001_idle_01.png
    spritesheets/
      patient_001.png
      clinician_back.png
    metadata/
      patient_001.json
      clinician_back.json
```

Runtime code should consume `spritesheets/*.png` plus `metadata/*.json`, not source files.

## Metadata Contract

Each sprite metadata file should follow this shape:

```json
{
  "id": "patient_001",
  "role": "patient",
  "pixelSize": 2,
  "sheet": "../spritesheets/patient_001.png",
  "frameWidth": 64,
  "frameHeight": 64,
  "states": {
    "idle": {
      "frames": [0, 1, 2, 3],
      "fps": 4,
      "loop": true
    },
    "discomfort": {
      "frames": [4, 5, 6, 7],
      "fps": 4,
      "loop": true
    },
    "critical": {
      "frames": [8, 9, 10, 11],
      "fps": 6,
      "loop": true
    }
  },
  "provenance": {
    "source": "manual | ai_generated_then_edited | community_asset",
    "license": "project_owned | reviewed_license_name",
    "promptFile": "optional/path/to/prompt.md"
  }
}
```

Do not encode hidden diagnosis, evaluator keys, or internal prompt content in filenames,
metadata, alt text, layer names, or prompts saved for presentation.

## Animation Contract

Start with CSS sprite animation:

- Use fixed frame dimensions and `image-rendering: pixelated`.
- Use CSS `steps(frame_count)` for idle and state loops.
- Keep a static first frame for screenshots, reduced motion, and loading fallback.
- Do not let animation move text, input controls, or clinical feedback out of view.

Move to PixiJS, Phaser, or canvas only if the CSS approach cannot support the interaction
requirements.

## AI Asset Generation Rules

AI-generated pixel art may be used as a draft, but it must be reviewed before runtime use.

Record:

- Prompt text.
- Tool or model used if known.
- Date generated.
- Manual edits applied.
- License or usage assumption.

Reject generated assets that:

- Look like copied Rhythm Doctor, Pokemon, Duolingo, or recognizable third-party characters.
- Use inconsistent pixel scale, anti-aliased edges, or blurred upscaling.
- Make the product look like a generic AI medical dashboard.
- Visually imply real diagnosis, emergency instruction, or treatment advice.

## Visual QA

Before accepting pixel assets:

- Check desktop and mobile screenshots.
- Confirm patient state is readable without relying only on color.
- Confirm sprite scale does not crowd transcript, input, or report controls.
- Confirm reduced-motion/static fallback works.
- Confirm asset provenance is recorded.

## Deferred Decisions

- Final art tool.
- Exact resolution and palette.
- Number of patient archetypes.
- Whether sprite generation is done by AI, manually, or mixed.
- Whether a rendering engine is introduced after MVP.
