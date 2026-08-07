"""
modules/
Feature modules. Each one implements core.contracts.IModule and
communicates with other modules ONLY through the event bus in core/.
Modules may depend on core/ and shared/, but never on each other directly.
"""
