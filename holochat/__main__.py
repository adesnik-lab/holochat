import argparse

import uvicorn

from holochat.settings import load_settings


settings = load_settings('config.json')
PORT = settings.server.port
HOST_IP = settings.server.ip
WORKERS = settings.server.workers


parser = argparse.ArgumentParser(description='Stimsync')
parser.add_argument('-l', action='store_true') # this will run on localhost despite the config file
args = parser.parse_args()


if args.run_local:
    uvicorn.run('holochat.main:app', host="localhost", port=PORT, reload=True)
else:
    uvicorn.run('holochat.main:app', host=HOST_IP, port=PORT, workers=WORKERS, log_level='warning')