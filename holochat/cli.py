import argparse
import importlib.metadata

import uvicorn

from holochat.settings import load_settings

def run_holochat():
    
    print('\n( h o l o c h a t )')
    print('v', importlib.metadata.version('holochat'), sep='')
    
    settings = load_settings()
        
    PORT = settings.server.port
    HOST_IP = settings.server.ip
    WORKERS = settings.server.workers

    parser = argparse.ArgumentParser(description='holochat')
    parser.add_argument('--debug', action='store_true', 
                        help='this will run on localhost despite the config file. also enables reload on uvicorn.')
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()

    if args.test:
        # print('\n )o(  holochat  )o(')

        print('\nrunning fake holochat...')
        print('i quit.')
    elif args.debug:
        uvicorn.run('holochat.main:app', host="localhost", port=PORT, reload=True)
    else:
        uvicorn.run('holochat.main:app', host=HOST_IP, port=PORT, workers=WORKERS)