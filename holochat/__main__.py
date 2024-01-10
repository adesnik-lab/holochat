import argparse

import uvicorn

from holochat.main import app
from holochat.settings import load_settings


settings = load_settings('config.json')
DEFAULT_PORT = settings.server.port
DEFAULT_IP = settings.server.ip


parser = argparse.ArgumentParser(description='Stimsync')
parser.add_argument('--port', default=DEFAULT_PORT, type=int)
parser.add_argument('--ip', default=DEFAULT_IP)
parser.add_argument('--run-local', action='store_true') # this will run on localhost despite the config file
args = parser.parse_args()


if args.run_local:
    uvicorn.run(app, host="localhost", port=args.port)
else:
    uvicorn.run(app, host=args.ip, port=args.port)