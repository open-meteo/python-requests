#[doc('list available recipies')]
default:
    just --list

#[doc('build the project')]
build:
    uv build

#[doc('check code')]
check:
    ruff format --check
    ruff check

#[doc('lint code')]
lint:
    ruff format
    ruff check --fix
    mypy

#[doc('install project main+dev deps')]
install:
    uv sync --group lint --group test

#[doc('run tests')]
test *args:
    pytest {{args}}
