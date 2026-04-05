# Double-digits Maintainer Guide

This directory is the canonical documentation set for maintainers of the `dd` repo.

Use it in this order when you need to understand or change the system:

1. [Overview](overview.md)
2. [Architecture](architecture.md)
3. [Interfaces](interfaces.md)
4. [Models and artifacts](models-and-artifacts.md)
5. [Operations](operations.md)

## What This Guide Covers

- the role of `dd` inside the AIX Project
- the package-level ownership boundaries inside the repo
- the data, runtime, visualization, web, and CLI flows
- the stable contracts a future maintainer should preserve
- the operational rules for artifacts, deployment, and mounted execution

## What This Guide Does Not Replace

The top-level `docs/` files are still useful as provenance and migration records:

- notebook-restoration rationale
- phase-by-phase implementation history
- detailed migration inventory from notebook code into the current repo

Treat those files as supporting evidence. Treat this `docs/maintainer/` directory as the primary maintainer path.
