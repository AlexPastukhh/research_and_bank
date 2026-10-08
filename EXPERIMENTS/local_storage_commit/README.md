# Synthetic local storage mechanism probe

Run from project root: `python EXPERIMENTS/local_storage_commit/probe.py`.
Requires native Python with SQLite STRICT tables and connection defensive-config API (tested version in work receipt).
Uses only disposable temporary DBs and child-process exit; never opens production Bank or powers off the computer.
Direct SQL intentionally bypasses Bank domain schema/secure intake validation; this proves database mechanisms only.
Candidate SQL and limit policy are in PLANNING/CONTRACTS. No UI/importer/media benchmark or physical power-loss acceptance.
