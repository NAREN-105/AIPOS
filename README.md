# AIPOS — AI-Powered OS Assistant (v1.0)

A modular, event-driven desktop assistant. v1.0 ships two feature modules —
**real-time system monitoring** and a **rule-based AI chat** — built on top
of a Core Engine designed to let unlimited future modules (Voice, Agents,
Memory, File Assistant) plug in **without ever modifying core code**.

```
You: how's my system doing?
AIPOS: CPU: 4.2% | RAM: 61.3% | Disk: 46.1%
```

## Why this project exists

Most beginner "modular" projects aren't actually modular — every module
quietly imports every other module, and the whole thing collapses the moment
you try to add a new feature. AIPOS is built the other way around: the
architecture was designed **before** any feature code was written, using the
same Dependency Rule that underlies Clean Architecture (Robert C. Martin).

## Architecture

```
┌─────────────┐                                   ┌──────────────┐
│  AI Chat     │──publish(USER_MESSAGE)──────────▶│              │
│  Module      │                                   │  Core Engine │
│              │◀───AI_REPLY─────────────────────  │ (Event Bus)  │
└─────────────┘                                    └──────┬───────┘
                                                            │ routes
                                                            ▼
                                                    ┌──────────────┐
                                                    │   System      │
                                                    │   Monitor     │
                                                    └──────────────┘
```

**The rule that makes this work:** modules never import or call each other
directly. They only publish/subscribe to `Event` objects through the
`EventBus` in `core/`. Concretely:

- `core/` depends on **nothing** outside itself — it only knows about the
  abstract `IModule` contract, never a concrete module (Dependency Inversion
  Principle).
- `modules/` depend on `core/` and `shared/`, but never on each other.
- `shared/` (Logger, Config) is the one exception — imported directly
  everywhere, since it carries no coupling or crash risk.

This gives two concrete guarantees, both proven by tests, not just claimed:

| Guarantee | How it's proven |
|---|---|
| **Fault isolation** — one module crashing can't crash the app | `tests/test_fault_isolation.py` registers a module that always raises, and asserts the bus keeps running and other modules still respond |
| **Extensibility** — new modules need zero changes to `core/` | Adding a module = implementing `IModule` + calling `bus.register()`; no existing file needs editing |

Full reasoning for each decision — including alternatives that were
considered and rejected — is written up as ADRs in [`docs/adr/`](docs/adr/).

## Features (v1.0)

- **System Monitor** — live CPU / RAM / disk usage via `psutil`
- **AI Chat** — rule-based assistant; ask it about your system and it
  fetches live stats from System Monitor *through the event bus*, not a
  direct function call
- **Runs fully offline** — no API keys, no network calls, no data leaves
  the machine (v1.0 deliberately avoids the trust/privacy risk of
  local-vs-cloud LLM integration — see `docs/adr/`)
- **Structured logging** — every event publish, route, and error is logged
  to `logs/aipos.log`
- **7 passing tests**, including a real fault-isolation proof

## Project structure

```
aipos/
├── core/                   # Innermost layer — knows nothing about modules
│   ├── contracts.py        # IModule interface + Event dataclass
│   └── event_bus.py        # Core Engine — the only thing modules talk to
├── shared/                 # Logger, Config — imported directly everywhere
│   ├── logger.py
│   └── config.py
├── modules/
│   ├── system_monitor/     # Real-time CPU/RAM/disk stats (psutil)
│   └── ai_chat/            # Rule-based chat, talks to system_monitor via bus
├── tests/
│   ├── test_event_bus.py
│   └── test_fault_isolation.py
├── docs/adr/                # Architecture Decision Records
├── config/settings.ini
└── main.py                  # Composition root — wires modules onto the bus
```

## Getting started

### Prerequisites
- Python 3.10+

### Run it

```bash
git clone <this-repo>
cd aipos
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Try asking it:
```
how's my system doing?
```

### Run tests

```bash
python -m pytest -v
```

## Adding a new module (this is the whole point)

1. Create `modules/your_module/your_module.py`
2. Implement `IModule`: give it a `name`, a `subscriptions()` list, and a
   `handle_event()` method
3. Register it in `main.py`: `bus.register(YourModule())`

That's it — `core/` never changes, and no existing module needs to know
your new module exists.

## Roadmap (post-v1.0)

- [ ] Voice Assistant module
- [ ] Memory module (persistent context across sessions)
- [ ] File Assistant module
- [ ] Local vs. cloud LLM integration, with an explicit user-visible
      boundary for what data (if any) leaves the machine
- [ ] GUI (currently CLI-only)

## License

MIT — see [LICENSE](LICENSE)
