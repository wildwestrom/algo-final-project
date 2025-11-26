# Priority Sorter

Interactive Tkinter application that helps users build a strict total order of
priorities using safe pairwise comparisons. The core algorithm is a binary insertion sort 
that never asks for implied comparisons, so contradictions are impossible.

## Quick start

### NixOS (or any system with flakes enabled)

```bash
# Enter the development shell (provides Python, uv, and Tkinter)
nix develop

# Install dependencies with uv
uv sync

# Run the application
uv run python main.py
```

### Debian/Ubuntu (other apt-based Linux distros)

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk pipx
pipx install uv  # or python3 -m pip install uv --user

python3 -m venv .venv
source .venv/bin/activate
uv sync
uv run python main.py
```

### macOS (Apple Silicon or Intel)

```bash
# Install Python 3.11+ (Homebrew shown here)
brew install python@3.11 uv tcl-tk

python3.11 -m venv .venv
source .venv/bin/activate
uv sync
uv run python main.py
```

### Windows (PowerShell)

```powershell
winget install Python.Python.3.11  # confirms python3 + pip
pip install --user uv

python -m venv .venv
.venv\Scripts\Activate.ps1
uv sync
uv run python main.py
```

Use the entry box to add priorities, edit/delete existing ones inline, then
press **Sort Items** to enter the comparison workflow. Left/right buttons
choose which item outranks the other; press `Esc` or the on-screen button to
return to the list view at any time.

## Tests

```bash
# From within the nix develop shell
uv run pytest
```

The test suite runs a deterministic simulation of thousands of insertions and
verifies we never exceed the theoretical comparison bound.

## Project layout

- `priority_sorter/sorter.py` – interactive insertion algorithm.
- `priority_sorter/gui.py` – Tkinter UI with list and comparison views.
- `priority_sorter/items.py` – item dataclass and default seeds.
- `tests/test_sorter.py` – algorithm regression tests.
- `spec.md` – original requirements and rationale.