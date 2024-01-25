import argparse
import importlib.metadata

import uvicorn

from holochat.settings import load_settings, save_settings


settings = load_settings()

PORT = settings.server.port
HOST_IP = settings.server.ip
WORKERS = settings.server.workers
APP_MODULE = 'holochat.main:app'


def setup_parser():
    parser = argparse.ArgumentParser(description='holochat: a RESTful api for running experiments.')
    subparses = parser.add_subparsers(dest='command')
    
    # setup command
    setup_parser = subparses.add_parser('setup', help='generate settings files')
    setup_parser.add_argument('--home', action='store_true', help="Also save to user's home directory.")
    setup_parser.add_argument('--ow', action='store_true', help="Overwrite existing file(s).")
    
    # run command
    run_parser = subparses.add_parser('run', help='run holochat server')
    run_parser.add_argument('--debug', action='store_true', 
                        help='this will run on localhost despite the config file. also enables reload on uvicorn.')
    
    return parser
        
def start_server(args: argparse.Namespace):
    print('Starting server...')
    if args.debug:
        print('Running in debug mode.')
        uvicorn.run(APP_MODULE, host="localhost", port=PORT, reload=True)
    else:
        uvicorn.run(APP_MODULE, host=HOST_IP, port=PORT, workers=WORKERS)

def run_holochat():
    """The function that runs everything."""
    
    print('\n( h o l o c h a t )')
    print('v', importlib.metadata.version('holochat'), sep='', end='\n\n')
    print("~ at least it's not msockets ~", end='\n\n\n')

    parser = setup_parser()
    args = parser.parse_args()
            
    if args.command == 'setup':
        save_settings(args.home, args.ow)
    elif args.command == 'run':
        start_server(args)
    else:
        print('WARNING! No command given. I guess we will just run it anyway?')
        start_server(args)