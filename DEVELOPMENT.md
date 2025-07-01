# Development

For convenience, you can install [Just](https://github.com/casey/just) to run recipes defined in the [Justfile](./Justfile). Feel free to read the [Just/docs](https://just.systems/man/en/)

You can create a virtual environment directory via the `uv venv` command (the version is retrieved from the **.python-version** file).

Dependency installation is done via `uv sync --group dev --group lint --group --test` or by executing the `just install` recipe.

Consider installing pre-commit hooks -> `pre-commit install`.
