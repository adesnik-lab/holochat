import argparse

import uvicorn

from holochat.settings import load_settings


settings = load_settings()
    
PORT = settings.server.port
HOST_IP = settings.server.ip
WORKERS = settings.server.workers

parser = argparse.ArgumentParser(description='holochat')
parser.add_argument('--debug', action='store_true', 
                    help='this will run on localhost despite the config file. also enables reload on uvicorn.')
args = parser.parse_args()


if args.debug:
    uvicorn.run('holochat.main:app', host="localhost", port=PORT, reload=True)
else:
    uvicorn.run('holochat.main:app', host=HOST_IP, port=PORT, workers=WORKERS)