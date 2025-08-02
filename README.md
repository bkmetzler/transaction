# Transaction

A lightweight Python 3.12+ library for tracking decorated function calls and supporting structured rollback logic.

## Features

- Sync + async support
- Rollback propagation (fail-fast)
- Per-task context isolation
- Export/import rollback state

## Usage

```python
@transaction
def step():
    ...

@step.rollback
def rollback_step():
    ...
