#!/usr/bin/env just --justfile

default:
    just --list

venv:
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -e .

prepare-data:
    .venv/bin/cjlib-bench prepare-data

build:
    .venv/bin/cjlib-bench build

run *args:
    .venv/bin/cjlib-bench run {{args}}

clean:
    rm -rf .venv build results data/generated
