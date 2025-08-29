# Abstract Machine Interpreter

A repository that contains an interpreter for abstract machines used in formal languages and automata coursework (Turing machines, finite automata, stack machines, and related variants).
This README gives a quick orientation to the codebase, how to run the interpreter on the provided examples in `test_cases/`, and useful next steps for contributors.

## Repository layout
- `CSC615M_Guanzon.py` — Main Python interpreter (entry point). This script parses machine description files and executes/simulates them.
- `test_cases/` — Example machine descriptions used for demonstration and quick testing. Filenames include many variants: single-tape and multi-tape Turing machines, one- and two-stack machines, two-way machines, nondeterministic examples, and more.

Selected example files in `test_cases/`:
- `sampleMachine(TM).txt`
- `sampleTwoTapeTM.txt`
- `OneWayOneStack.txt`
- `OneWayTwoStack.txt`
- `TwoWayAccepter.txt`
- `withPrint.txt`

## Purpose

The codebase is intended for:
- exploring abstract computation models.
- Running / tracing example machines from `test_cases/`.
- Extending with additional machine types, parsers, or visualizers.

## How to run (examples)

From the repository root (macOS / zsh):

```bash
# Run the GUI
python3 CSC615M_Guanzon.py
```

Then place the text from the sample test cases into the text input for it to be ready to get interpreted.

Notes:
- If you see syntax or import errors, ensure your Python version is 3.8 or newer (`python3 --version`).

## What the output looks like

Output varies by the implementation and the machine description. Typical outputs from example machines may include:
- Acceptance / rejection messages.
- Final tape contents.
- Transition traces or step-by-step traces for debugging.

Open the example file to see any embedded comments that control printing or verbosity.

## Troubleshooting

- Python errors: check `python3 --version` and run under a supported Python.
- If the machine does not behave as expected, inspect the transition format in the example file and the parser in `CSC615M_Guanzon.py`.
