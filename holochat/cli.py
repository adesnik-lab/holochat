import argparse
import importlib.metadata

import uvicorn

from holochat.settings import (REPO_JSON_PATH, SCHEMA_PATH, USER_JSON_PATH,
                               generate_schema, generate_settings,
                               load_settings)


def run_holochat():
    
    print('\n( h o l o c h a t )')
    print('v', importlib.metadata.version('holochat'), sep='', end='\n\n\n')
    
    settings = load_settings()
        
    PORT = settings.server.port
    HOST_IP = settings.server.ip
    WORKERS = settings.server.workers

    parser = argparse.ArgumentParser(description='holochat: way better than msocket.')
    parser.add_argument('-t', '--test', action='store_true')
    subparses = parser.add_subparsers(dest='command')
    
    setup_parser = subparses.add_parser('setup', help='generate settings files')
    setup_parser.add_argument('--home', action='store_true', help="Also save to user's home directory.")
    setup_parser.add_argument('--ow', action='store_true', help="Overwrite existing file(s).")
    
    run_parser = subparses.add_parser('run', help='run holochat')
    run_parser.add_argument('--debug', action='store_true', 
                        help='this will run on localhost despite the config file. also enables reload on uvicorn.')
    
    args = parser.parse_args()
    
    if args.test:
        print('\nrunning fake holochat...')
        print('i quit.')
            
    elif args.command == 'setup':
        if args.home:
            print('Generating settings file at user home...')
            generate_settings(USER_JSON_PATH, overwrite=args.ow, with_schema=False)
            
        else:
            print('Generating schema and settings file in repo...')
            generate_schema(SCHEMA_PATH, overwrite=args.ow)
            generate_settings(REPO_JSON_PATH, overwrite=args.ow, with_schema=True)
        print('Done.')
        
    elif args.command == 'run':
        if args.test:
            print('\nrunning fake holochat...')
            print('i quit.')
        elif args.debug:
            uvicorn.run('holochat.main:app', host="localhost", port=PORT, reload=True)
        else:
            uvicorn.run('holochat.main:app', host=HOST_IP, port=PORT, workers=WORKERS)
            
    else:
        parser.print_help()
        
        
        

    
