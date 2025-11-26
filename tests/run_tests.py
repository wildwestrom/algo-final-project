from __future__ import annotations

import importlib
import inspect
import sys
import traceback
from types import FunctionType


def _discover(module_name: str) -> list[tuple[str, FunctionType]]:
    module = importlib.import_module(module_name)
    tests: list[tuple[str, FunctionType]] = []
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("test_"):
            tests.append((name, func))
    tests.sort(key=lambda pair: pair[0])
    return tests


def _run_tests(tests: list[tuple[str, FunctionType]]) -> int:
    failures = 0
    for name, func in tests:
        try:
            func()
        except AssertionError:
            failures += 1
            print(f"FAIL: {name}")
            traceback.print_exc()
        except Exception:
            failures += 1
            print(f"ERROR: {name}")
            traceback.print_exc()
        else:
            print(f"PASS: {name}")
    total = len(tests)
    print(f"Ran {total} test{'s' if total != 1 else ''}.")
    if failures:
        print(f"{failures} failure{'s' if failures != 1 else ''}.")
    else:
        print("All tests passed.")
    return failures


def main() -> int:
    tests = _discover("tests.test_sorter")
    if not tests:
        print("No tests discovered.")
        return 1
    return 1 if _run_tests(tests) else 0


if __name__ == "__main__":
    sys.exit(main())

