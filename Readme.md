# Aladhan Api and Frontend

## Install the app

Make sure you have [uv](https://docs.astral.sh/uv/guides/install-python/)

- Before installing the app run data_tools

```shell
cd data_tools
uv sync
uv run python main.py

```

- frontend:

```shell
cd frontend
yarn install
```

- backend

```shell
cd backend
uv sync
```

## RUN the app

- front :

```shell
cd frontend
yarn build --watch
```

- backend (in another terminal)

```shell
cd backend
uv run uvicorn src.main:app --reload --host 127.0.0.1 
```
