# ADR-003: Dependency Rule (Clean Architecture)

**Status:** Accepted

## Context
Without an enforced rule about which layer can import which, it's easy
for `core/` to accidentally depend on a specific module's internals,
which would make `core/` unreusable and fragile.

## Decision
Dependencies point inward only:

```
modules/  -->  core/
modules/  -->  shared/
core/     -->  (nothing outside itself)
shared/   -->  (nothing outside itself)
```

`core/` never imports from `modules/`. It only depends on the abstract
`IModule` contract (`core/contracts.py`) — this is the Dependency
Inversion Principle (the "D" in SOLID).

`shared/` utilities (Logger, Config) are the one exception to the event
bus: they carry no coupling or crash risk, so every layer imports them
directly rather than routing trivial calls through the bus.

## Consequences
- New modules can be added by implementing `IModule` — zero changes to
  `core/` are ever required.
- `core/` could be lifted into a different project unmodified.
- Enforced by code review / convention in v1.0; a lint rule (e.g.
  import-linter) is a natural addition for v1.1+.
