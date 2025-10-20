# Aladhan Api and Frontend Beta version 0.1.0

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

## For Devs

### RUN the app

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

## Docker env

- Docker :

Clone in your device data_tools first and run it

Note : in the future it will be included in docker when it runs for the first time.

```shell
uv sync
uv run python main.py
```

Make sure you have a folder data with cities.db in it and some adhan.mp3 files maybe here : [call to prayer files](https://www.assabile.com/adhan-call-prayer)

```shell
docker run -d   --name adhan-api   --network host   -v /etc/localtime:/etc/localtime:ro   -v /etc/timezone:/etc/timezone:ro   -v /home/pi/data:/app/src/data  aminekun90/adhan-api
```
