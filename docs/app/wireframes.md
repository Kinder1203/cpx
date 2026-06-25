# Wireframes

텍스트 와이어프레임은 프레임워크 결정 전 layout contract다. 실제 구현 전에는
Figma나 코드 기반 UI에서 이 구조를 다시 검증한다.

## Desktop MVP

```text
┌────────────────────────────────────────────────────────────────────┐
│ CODE MEDI CPX                         Case: Safe metadata only      │
├───────────────────────┬────────────────────────────────────────────┤
│ Case Setup            │ Encounter                                  │
│ - Card status         │ ┌────────────────────────────────────────┐ │
│ - Required fields     │ │ transcript messages                    │ │
│ - Start / Reset       │ │ patient answers                        │ │
│                       │ └────────────────────────────────────────┘ │
│ Safety Flags          │ [ student question input              ][>] │
│ - no hidden diagnosis │                                            │
├───────────────────────┴────────────────────────────────────────────┤
│ Evaluation Report: checklist coverage | missed items | safety notes │
└────────────────────────────────────────────────────────────────────┘
```

## Mobile MVP

```text
┌──────────────────────────────┐
│ CODE MEDI CPX                │
│ Case status + session state  │
├──────────────────────────────┤
│ Transcript                   │
│                              │
├──────────────────────────────┤
│ Input + send                 │
├──────────────────────────────┤
│ Evaluation tab after finish  │
└──────────────────────────────┘
```

## Pixel Serious Simulation Desktop

```text
+--------------------------------------------------------------------------------+
| CODE MEDI CPX Mission        Safe case metadata            Stability Trust Risk |
+---------------------------+----------------------------------------------------+
| Mission Map / Case Brief   | Patient sprite + response bubble                  |
| - mission objective        |        [upper-left patient]                       |
| - skill focus              |                                                    |
| - card validation          |                                                    |
| - safe warnings            |                         [lower-right doctor back] |
+---------------------------+----------------------------------------------------+
| Question cards / free-input assist / selected action                            |
+--------------------------------------------------------------------------------+
| Transcript drawer or compact log                         End | Decision Board   |
+--------------------------------------------------------------------------------+
| CPX Report after finish: checklist | missed red flags | communication | next     |
+--------------------------------------------------------------------------------+
```

The encounter scene is the signature surface. The transcript supports the scene but should
not make the product feel like a plain chatbot.

## Interaction Notes

- Case setup and evaluation may be tabs on small screens.
- Encounter input must stay visible and must not overlap transcript content.
- Hidden/internal fields are never rendered as labels, tooltips, raw JSON, debug panels, or
  downloadable artifacts.
- If a visual design system is adopted, this wireframe remains the minimum information
  architecture.
