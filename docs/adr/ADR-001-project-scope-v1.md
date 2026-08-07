# ADR-001: AIPOS v1.0 Scope

**Status:** Accepted

## Context
AIPOS's full vision includes many future modules (Voice Assistant, Agents,
Memory, File Assistant, etc.). Building all of them at once risks the
project never shipping and makes the architecture harder to validate.

## Decision
v1.0 ships with exactly two feature modules:
- `system_monitor` — real-time CPU/RAM/disk stats via `psutil`
- `ai_chat` — rule-based assistant (no external API key required)

Everything else (Voice, Agents, Memory, File Assistant, GUI) is explicitly
out of scope for v1.0.

## Consequences
- v1.0 is small enough to fully test and reason about.
- The two modules chosen are enough to prove the core architectural claim:
  modules communicating only through the event bus, with fault isolation.
- Runs fully offline — no API keys, no data leaves the machine — directly
  addressing the trust/privacy risk identified during requirements review.
