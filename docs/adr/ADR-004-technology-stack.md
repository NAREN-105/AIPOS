# ADR-004: Technology Stack

**Status:** Accepted

## Decision
- Core language: Python 3
- Future GUI (Dashboard): PySide6
- Configuration: INI/JSON files for v1.0
- AI backend: swappable behind the AI Chat module interface; local-first
  (e.g. Ollama) is the leading candidate for v1.1
- Persistence: no database until the Memory module (v2.0), then SQLite
- Distribution: run from source for v1.0, no installer yet

## Reasoning
- Fits the existing tested MVP and the IModule/event bus design.
- Matches current skill level and has a strong AI/system-monitoring ecosystem.
- Defers GUI, LLM integration, persistence and packaging until each is needed (YAGNI).

## Alternatives Rejected
Electron/TypeScript (steep learning curve now), Tkinter (weaker live UI),
web-based local UI (unnecessary complexity), cloud-only AI (conflicts with
privacy goals), database now (premature).