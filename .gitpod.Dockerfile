# hadolint ignore=DL3007
FROM gitpod/workspace-full:latest

RUN pyenv install 3.10.4 && pyenv global 3.10.4
# hadolint ignore=DL4006
RUN curl -sSL https://install.python-poetry.org | python3 - --yes --force
