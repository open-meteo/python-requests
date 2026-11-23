# Development

For convenience, you can install [Just](https://github.com/casey/just) to run recipes defined in the [Justfile](./Justfile). Feel free to read the [Just/docs](https://just.systems/man/en/)

You can create a virtual environment directory via the `uv venv` command (the version is retrieved from the **.python-version** file).

Dependency installation is done via `uv sync --group dev --group lint --group test` or by executing the `just install` recipe.

Consider installing pre-commit hooks -> `pre-commit install`.

## Releasing to PyPI

Create a GitHub Actions environment named `pypi` in `open-meteo/python-requests`. In the [PyPI project's publishing settings](https://pypi.org/manage/project/openmeteo-requests/settings/publishing/), add a GitHub Trusted Publisher with these values.

| Field | Value |
| --- | --- |
| Owner | `open-meteo` |
| Repository | `python-requests` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

Run the **Release** workflow manually from `main`. When semantic-release determines a new version, the workflow builds the wheel and source distribution, creates the GitHub release, and publishes both files with PyPI publish attestations. If the PyPI job fails after the GitHub release is created, rerun that job from the same workflow run to reuse the built distributions.
