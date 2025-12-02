# Mortgage Rule Engine

YAML-driven mortgage validation engine.

## Overview
- Rules defined in `app/config/rules.yaml`.
- Field paths + defaults in `app/config/fields.yaml`.
- Single validators file: `app/validators/validators.py`.
- Engine entry point: `app/api/routes.py` (POST /validate).

## Quickstart
1. Create venv and install deps:
"# agent-2.2" 
