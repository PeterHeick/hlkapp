---
name: python-standards
description: Apply project conventions for Python code — Python 3.12+, uv, src-layout, hatchling, Ruff, mypy, pytest, pydantic-settings. Auto-invoke when creating, structuring, or reviewing Python projects, when working with .py files, pyproject.toml, uv.lock, requirements.txt, or when discussing Python package structure, dependencies, linting, formatting, type checking, testing, logging, or configuration. Do NOT load for Node, TypeScript, Vue, or C++ projects.
---

# Python Standarder

Følg disse konventioner for alle Python-projekter. Python 3.12+ er minimum.

## Tooling — eksplicit valg

| Område | Værktøj | Note |
|---|---|---|
| Package manager | **uv** | Erstatter pip, pip-tools, virtualenv, pipx, pyenv |
| Build backend | **hatchling** | Modern default i `pyproject.toml` |
| Linter/formatter | **Ruff** | Erstatter Black, Flake8, isort, pyupgrade |
| Type checker | **mypy** | Altid slået til, ikke valgfrit |
| Test framework | **pytest** | Med pytest-cov til coverage |
| Config/secrets | **pydantic-settings** | Type-sikker `.env`-loading |
| Pre-commit | **pre-commit** | Ruff + mypy kører lokalt før commit |

## Projekt-struktur (src-layout)

```text
projekt-navn/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── conftest.py         # Fælles fixtures
│   └── test_main.py
├── .python-version         # uv læser denne
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock                 # SKAL committes
├── .env.example
└── README.md
```

## `pyproject.toml` — minimum-skelet

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "package_name"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]                     # PEP 735, ikke optional-dependencies
dev = ["pytest", "pytest-cov", "ruff", "mypy", "pre-commit"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "RUF"]

[tool.mypy]
strict = true
python_version = "3.12"

[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing"
testpaths = ["tests"]
```

Strikshed kan lempes på prototyper (`mypy: strict = false`), men type checking slås aldrig helt fra.

## Kode-konventioner

- **Typing:** Type hints på alle public funktioner og metoder. Brug 3.12 syntax: `list[str]` ikke `List[str]`, `X | None` ikke `Optional[X]`, `type Alias = ...` ikke `TypeAlias`.
- **Docstrings:** Google-stil. Public API skal have docstrings; trivielle private helpers kan undvære.
- **Logging:** Brug `logging`-modulet. **Aldrig `print()` i bibliotekskode eller production-paths** — kun acceptabelt i CLI-output beregnet til brugeren eller i throwaway scripts.
- **Konfiguration:** Brug `pydantic-settings.BaseSettings` til at loade `.env` og environment variables. Aldrig `os.environ[...]` spredt rundt i koden.
- **Async:** Hvis projektet er async, så *konsekvent* async — bland ikke sync og async I/O i samme code path.

## Test-konventioner

- Tests spejler `src/`-strukturen i `tests/`.
- Fælles fixtures i `tests/conftest.py` — duplikér aldrig fixtures på tværs af filer.
- Coverage minimum 80 % på ny kode (hård tærskel i CI).
- Test-navne: `test_<beskrivende_handling>`, ikke `test_1`, `test_function`.

## Workflow-kommandoer (uv)

```bash
uv init --package              # Nyt projekt med src-layout
uv add <pakke>                 # Tilføj runtime dependency
uv add --dev <pakke>           # Tilføj dev dependency
uv sync                        # Synk environment med lockfile
uv run pytest                  # Kør i projektets venv
uv run ruff check --fix .      # Lint + auto-fix
uv run mypy src                # Type check
```

## Anti-patterns — gør IKKE dette

- ❌ `requirements.txt` som primær dependency-fil (kun OK som eksport-format til Docker/CI)
- ❌ `setup.py` eller `setup.cfg` (forældet — alt i `pyproject.toml`)
- ❌ Bland uv med pip, poetry eller pipenv i samme projekt
- ❌ `[project.optional-dependencies].dev` til dev-tools (brug `[dependency-groups]`)
- ❌ Black, Flake8, isort, pyupgrade som separate værktøjer (Ruff dækker alle fire)
- ❌ Commit `__pycache__/`, `.venv/`, `*.pyc`, `.pytest_cache/` — alt skal i `.gitignore`
- ❌ Ikke-committet `uv.lock` (reproducerbarhed kræver låste dependencies)
- ❌ `from module import *` (eksplicit imports altid)

## Note for fullstack-projekter

Hvis Python er backend i et monorepo, ligger koden i `/server/` med eget `pyproject.toml` og `uv.lock` — aldrig delt med en eventuel frontend.