# hadolint ignore=DL3007
FROM gitpod/workspace-python-3.10:latest

# hadolint ignore=DL4006
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME="${HOME}/.poetry" python3 - --yes --force
