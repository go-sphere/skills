# Reference: Proto Output Template Index

## Purpose

Select the smallest final-output template that fits the task.

## When To Load

Load this reference only when preparing the final deliverable shape.
Do not load output templates during initial reasoning unless the task is specifically about output format.

## Selection Rule

1. Use [proto-output-condensed-template.md](proto-output-condensed-template.md) for straightforward CRUD or low-ambiguity API work with clear reuse and routing decisions.
2. Use [proto-output-full-template.md](proto-output-full-template.md) for custom business logic, multiple services, complex routing, explicit error design, or substantial validation commentary.
3. Load exactly one template unless you are explicitly comparing output shapes.

## Guardrails

1. Keep drafting notes separate from the final deliverable.
2. `Mandatory Confirmation` is allowed only when the checklist passes.
3. If a required check fails, output `Validation Notes -> Blocking Issues` instead of a success confirmation.
