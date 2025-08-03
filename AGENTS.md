# Contributor Guide

## Dev Environment Tips
- To setup the development environment, run 'pip install -e .[dev]'.
- 
- Run pnpm install --filter <project_name> to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
- Use pnpm create vite@latest <project_name> -- --template react-ts to spin up a new React + Vite package with TypeScript checks ready.
- Check the name field inside each package's package.json to confirm the right name—skip the top-level one.

## Testing Instructions
- Use pre-commit to run code verification in 'transaction' and 'tests' directories.
- For information on how to run tests, refer to '.github/workflows/nox.yaml' on how to run 'nox'
- Fix any test or type errors until the whole suite is green.
- Add or update tests for the code you change, even if nobody asked.

## PR instructions
Title format: [<project_name>] <Title>