# Pixel Asset Pipeline

This document defines the runtime contract for the current 2D pixel CPX assets.

## Decision Status

- Status: first static runtime asset set produced.
- Runtime: individual PNG files under `app/assets/pixel/`.
- Rendering: CSS backgrounds with `image-rendering: pixelated`.
- Heavy game engine: not required.

## Current Assets

```text
app/assets/pixel/
  clinic_room.png
  patient_idle.png
  learner_idle.png
  learner_typing.png
  learner_think.png
  coach_idle.png
  coach_write.png
```

Only referenced runtime assets belong in this folder. Replaced drafts and generated preview
output belong outside the runtime tree and should not be committed.

## Future Metadata Contract

Introduce spritesheets only when multiple animation frames are needed. Each sheet must have
metadata containing `id`, frame dimensions, named states, fps, loop behavior, and
`provenance` with source and license. CSS `steps()` remains the first animation option.

Do not encode hidden diagnosis, evaluator keys, or prompt content in filenames, metadata,
alt text, or saved prompts.

## QA

- Check desktop and Android viewport screenshots.
- Confirm pixel assets are sharp at runtime scale.
- Confirm sprites do not cover dialogue, input, or report controls.
- Provide static and reduced-motion behavior before adding animation.
- Record provenance and license before accepting generated or community assets.
