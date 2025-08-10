# list available rules
default:
    just --list

# build the project
build:
    uv build

# install project deps
install:
    uv sync --group dev --group lint --group test

# check code
check:
    ruff format --check
    ruff check
    mypy

# format and lint code
lint *files=".":
    ruff format
    ruff check --fix

# run tests
test *args:
    pytest {{args}}
