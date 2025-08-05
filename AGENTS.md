# Contributor Guide

## Dev Environment Tips
- To set up the development environment, run `pip install -e .[dev]`.

## Testing Instructions
- Use pre-commit to run code verification in `transaction` and `tests` directories.
- For information on how to run tests, refer to `.github/workflows/nox.yaml` for instructions on running `nox`.
- Fix any test or type errors until the whole suite is green.
- Add or update tests for the code you change, even if nobody asked.

## PR instructions
- Title format: [<project_name>] <Title>
