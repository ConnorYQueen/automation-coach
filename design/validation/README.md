# Validation harness for the design folder

These scripts check the three JSON Schemas, every JSON example and every engine fixture in the
design documents against a real validator. They exist so the specs cannot drift away from the
schemas without somebody noticing.

## Setup (once)

Create a throwaway virtual environment outside the design folder and install the pinned library.
On Windows keep the venv path short (a long path fails with WinError 267).

    python -m venv <short-path>/coach-jsonschema-venv
    <short-path>/coach-jsonschema-venv/Scripts/python -m pip install -r requirements.txt

The pin is `jsonschema[format-nongpl]==4.26.0` on Python 3.12. The `format-nongpl` extra turns on
format checks (date-time, uri and so on) without pulling in GPL-licensed packages.

## Run

    <venv>/Scripts/python run_all.py

`DESIGN_DIR` (environment variable) points at the folder that holds the schemas and documents. It
defaults to the parent of this folder. The exit code is 0 only when both gating checks pass.

| Script | What it does | Gates? |
|---|---|---|
| `validate_docs.py` | Meta-validates the five schemas (Blueprint, connection, policy, CapabilityReport, coach session) and the 28 coach tool parameter schemas, then validates the tool catalog seed, every JSON example in `rules-engine.md`, `settings-catalog.md`, `coach-spec.md` and `model-certification.md`, and every engine fixture (rebuilt into a full Step with its diagnostic, environment and expected result) | yes |
| `check_cases.py` | Accept/reject cases: instances that must validate and instances that must not (audit entries, reopen marker, test status, confirmed-card rule, approved-status and attractor-check rules, policy locks, connection endpoints, CapabilityReport label and mode rules, SessionState, LiteExtract) | yes |
| `probe_untyped.py` | Deletes or retypes every leaf of each example and reports which changes the schema still accepts. Informational | no |
| `common.py` | Loads the schemas into one registry so `$ref` between schema files resolves by `$id` | n/a |

## Deliberate behavior the cases pin down

* An unknown audit `action` is accepted. `x-actions` documents the known names; older clients must
  not reject a log written by a newer one.
* An unknown policy setting key is accepted and ignored, for the same reason.

## What this does not cover

* Fixtures are checked for being well formed, not for producing the stated verdict. Running the
  rules engine against them is the job of the engine's own test suite once it exists.
* Rules that compare two fields (a probe's `passed` not exceeding `trials`, a lite follow-up being
  20 words or fewer, a `quote` being a substring of the user's message) cannot be written in JSON
  Schema. The host checks them, and so must its tests.
* The two coach schemas fix some values the specs never did (answer outcomes, document states,
  `teachLevel`, `pace`, `capReason` names and so on). The owner accepted them on 2026-10-26; see
  contract section 10.
