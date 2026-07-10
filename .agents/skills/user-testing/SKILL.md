---
name: user-testing
description: Use when finishing a user-facing/frontend feature, to verify it actually works for the person it's built for — not just that automated tests pass. Drives the real rendered UI via automation — browser tools (e.g. chrome-devtools) for web/HTML, platform UI automation for non-HTML native UI — through the actual user workflows, screenshotting each step and checking console/network, to catch defects unit/contract tests miss. A human hand-off is the optional gold standard. Distinct from test-quality (automated tests), spec-conformance (spec vs implementation), and review (code review).
---

# User Testing

## Intent

A frontend feature is not done because its automated tests pass. Automated tests assert code contracts (an element exists, an endpoint returns 200, a tab switches); they do not assert that the feature works or looks right for the person it's built for. Spec-conformance is not a substitute either — the spec itself can be wrong; only driving the real UI tells you. The primary method is tool-driven: the agent drives the real rendered UI (browser automation for web/HTML, platform UI automation for non-HTML native UI), so user testing is scalable and not dependent on a human being free. A human hand-off is the gold standard, not the only way.

## When to use

- Before declaring done (or closing) any user-facing/frontend change: a screen, tab, form, flow, layout, or anything a human sees or interacts with.
- When asked "did you user-test this?" or "does this actually work?"
- When automated tests are green but the feature has not been used as a user would use it.

## When it can't run ("when possible")

User testing may be impossible: no UI runtime, headless/CI-only, no user available. Then the closeout item is `blocked` with the reason recorded — never silently skipped. A functional smoke ("it loads, tabs switch") is the floor, not a substitute, and must be labeled as such.

## Workflow

**Data isolation (hard rule):** run user-testing against a throwaway/isolated data location (e.g. a temp database or test profile), **never the user's real environment data** — browser automation driving real user data can destroy it, and under unattended/orchestrated runs there is nobody watching to stop it.

1. **Enumerate the real user workflows** the feature serves (e.g., search → preview → add-to-playlist; pick-a-vibe → matches; dedup "only new"). These come from the spec's scenarios or the feature's intent — not from the test list.
2. **Drive the real UI via automation** — web/HTML: browser automation such as chrome-devtools (`navigate_page`, `click`, `fill`, `take_snapshot`, `take_screenshot`, `list_console_messages`, `list_network_requests`); non-HTML native UI (mobile/desktop): the platform's UI-automation tooling. Exercise each workflow end-to-end as the user would.
3. **Screenshot each step** and inspect with a user's eyes: empty columns, broken layouts, wrong copy, dead controls, things that take effort to notice.
4. **Check the runtime, not just the pixels**: console errors, failed network requests, missing/empty data — defects invisible to unit and contract tests.
5. **Flag anything** broken, wrong-looking, or harder than it should be — the defects automated tests miss.
6. **Human hand-off (optional — gold standard)**: if the actual user is available, hand it off and log what they hit. Tool-driven testing is the scalable default; a real user is the strongest signal, not the only one.
7. **Produce a user-test record**: workflows exercised, outcome + screenshots per step, issues found, and anything that couldn't be tested + why.

## Output

A user-test record (e.g., `docs/user-testing/<feature>.md` or a closeout section):
- workflows exercised (each: steps, result, screenshot refs)
- issues found (each: severity, what + where, screenshot)
- `not_tested`: what couldn't be tested + why (blocked), or "handed to user — pending"

## Non-goals

- Do not replace automated tests (`test-quality`) or spec-conformance (`spec-conformance`) — necessary, not sufficient.
- Do not judge code quality (Deep Review / `maintainability-review`).
- Do not fix issues found; report them so they become follow-up tasks.
