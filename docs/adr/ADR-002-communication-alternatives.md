# ADR-002: Alternatives Considered for Inter-Module Communication

**Status:** Accepted

## Options Considered

### 1. Direct method calls between modules
`ai_chat.py` imports and calls `system_monitor.get_cpu()` directly.
**Rejected** — creates tight coupling; a crash or change in one module
breaks others; does not scale past a handful of modules.

### 2. Shared global state
A single mutable object all modules read/write.
**Rejected** — any module can silently affect any other module's data;
bugs become nearly untraceable.

### 3. Microservices (each module as a separate networked process)
**Rejected for v1.0** — AIPOS is a single-user desktop app; the network
and operational overhead of microservices is pure cost with no benefit
at this scale (YAGNI). May be revisited if AIPOS becomes a distributed
cloud+desktop hybrid in a future major version.

## Decision
Event-driven, in-process communication via a Core Engine (`core/event_bus.py`).
Modules implement `IModule` and communicate exclusively by publishing/
subscribing to `Event` objects — never by importing each other directly.

## Consequences
- Loose coupling: modules can be added/removed without touching others.
- Fault isolation: a crash inside one module's `handle_event` is caught
  by the bus and reported as a `MODULE_ERROR` event, not propagated.
- Slight indirection cost (events instead of direct calls) — acceptable
  trade-off for the maintainability gained.
