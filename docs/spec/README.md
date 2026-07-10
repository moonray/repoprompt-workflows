# Spec Index

Canonical behavioral contracts. Each spec describes *what* and *why*; plans (derived separately) describe *how* and *when*.

| Spec | Issue | Status |
|------|-------|--------|
| [Spec Generation Workflow](spec.md) | none | implemented |
| [Test Generation Workflow](test.md) | none | implemented |
| [Loop Workflow](loop.md) | none | implemented |
| [Backlog Workflow](backlog.md) | none | implemented |
| [Deep Review Workflow](deep-review.md) | none | implemented |
| [Document Skill](document.md) | none | implemented |
| [Spec Quality Skill](spec-quality.md) | none | implemented |
| [Spec-Plan Readiness Skill](spec-plan-readiness.md) | none | implemented |

## Conformance matrices

Each spec has a sibling `<spec>.conformance.md` — a section-by-section audit (Conformed / Diverged / Not-built, with coverage proof) produced by the `spec-conformance` skill, showing the spec matches its implementation. Current matrices: [`deep-review`](deep-review.conformance.md), [`document`](document.conformance.md), [`loop`](loop.conformance.md), [`backlog`](backlog.conformance.md), [`spec`](spec.conformance.md), [`spec-quality`](spec-quality.conformance.md), [`spec-plan-readiness`](spec-plan-readiness.conformance.md), [`test`](test.conformance.md) — all fully conformed (every section Conformed, with no Diverged or Not-built items).
