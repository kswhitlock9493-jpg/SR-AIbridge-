# Firewall Allowlist

This directory contains allowlist configuration for GitHub Copilot agents during CI/CD runs.

## Purpose

The `hosts.txt` file is generated during the PreFlight workflow and contains domains that should be accessible before firewall enforcement.

## Auto-Generated Files

- `hosts.txt` - Created during workflow execution, contains allowed domains

## Usage

These files are automatically managed by the Copilot PreFlight workflow (`.github/workflows/copilot-preflight.yml`).
