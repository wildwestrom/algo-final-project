# Priority Sorter

Interactive Tkinter application that helps users build a strict total order of
priorities using safe pairwise comparisons. The core algorithm is a binary insertion sort 
that never asks for implied comparisons, so contradictions are impossible.

## Running

### Requirements

- Python 3 (tkinter is included by default)

### Running the application

```bash
python main.py
```

### NixOS (or any system with flakes enabled)

```bash
# Enter the development shell (provides Python and Tkinter)
nix develop

# Run the application
python main.py
```

### Debian/Ubuntu (other apt-based Linux distros)

```bash
sudo apt update
sudo apt install python3 python3-tk

python3 main.py
```

### macOS (Apple Silicon or Intel)

```bash
# Python 3 comes with macOS, or install via Homebrew
brew install python3 tcl-tk

python3 main.py
```

### Windows

```powershell
# Python 3 includes tkinter by default
python main.py
```

If you already have python set up, you might just be able to double click on
`main.py` and have it open up.

## Usage

Use the entry box to add priorities, edit/delete existing ones inline, then
press **Sort Items** to enter the comparison workflow. Left/right buttons
choose which item outranks the other; press `Esc` or the on-screen button to
return to the list view at any time.

## Tests

```bash
# Built-in runner that only needs the Python standard library
python tests.py
```

```bash
# (Optional) If you already have pytest installed:
pytest
```

The test suite runs a deterministic simulation of thousands of insertions and
verifies we never exceed the theoretical comparison bound.

## Project layout

- `priority_sorter/sorter.py` – interactive insertion algorithm.
- `priority_sorter/gui.py` – Tkinter UI with list and comparison views.
- `priority_sorter/items.py` – item dataclass and default seeds.
- `tests/test_sorter.py` – algorithm regression tests.
- `spec.md` – original requirements and rationale.
