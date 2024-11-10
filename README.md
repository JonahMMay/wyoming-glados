# Wyoming GLaDOS

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [GLaDOS](https://github.com/R2D2FISH/glados-tts) text to speech system from R2D2FISH. It uses CUDA acceleration if supported.

The server part is an heavily stripped down version of [wyoming-piper](https://github.com/rhasspy/wyoming-piper) and the gladostts folder is a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) of R2D2FISH's repo

TODOS: 
- Docker image ✅
- Automatic download of model files ✅ (please use download.py)
- Readme steps for connecting this to homeassistant - in progress
- Code cleanup
- Speedup the tts engine for rtx gpus ? See [here](https://developer.nvidia.com/tensorrt)

## How to run locally

```
git clone --recurse-submodules https://github.com/JonahMMay/wyoming-glados # You will probably get a git lfs error, this is fine
cd wyoming-glados
python3 -m venv .venv
source .venv/bin/activate
python3 download.py
pip install -r requirements.txt
python __main__.py --uri tcp://0.0.0.0:10201
```

## Docker Image

### docker-compose (recommended)
```
git clone --recurse-submodules https://github.com/JonahMMay/wyoming-glados # You will probably get a git lfs error, this is fine
cd wyoming-glados/docker
docker compose up -d
```

## Connecting to Home Assistant
1. Go to Settings -> Devices & Services
2. Add Integration -> Wyoming Protocol
3. Enter the IP and Port, click Submit
