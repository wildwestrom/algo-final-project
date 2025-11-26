from __future__ import annotations

import sys
import tkinter as tk

from priority_sorter import run_app


def main() -> None:
    try:
        run_app()
    except tk.TclError as exc:  # pragma: no cover - only hit on missing Tk installation
        message = (
            "Tkinter failed to initialize. Ensure the Tk GUI toolkit is installed.\n"
            f"Original error: {exc}"
        )
        print(message, file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
