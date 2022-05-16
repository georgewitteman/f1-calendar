FROM gitpod/workspace-full:latest

RUN pyenv install 3.10.4 && pyenv global 3.10.4
RUN curl -sSL https://install.python-poetry.org | python3 - --yes --force
