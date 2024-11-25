import argparse
import importlib.metadata
import socket

import httpx
import uvicorn
from colorama import just_fix_windows_console

from holochat.settings import load_settings, save_settings


just_fix_windows_console()

settings = load_settings()

PORT = settings.server.port
HOST_IP = settings.server.ip
WORKERS = settings.server.workers
APP_MODULE = 'holochat.main:app'

HC_VERSION = importlib.metadata.version('holochat')


def run_holochat():
    """The function that runs everything."""
    parser = setup_parser()
    args = parser.parse_args()
            
    if args.command == 'setup':
        print('holochat v', HC_VERSION, sep='')
        print('Run setup...')
        save_settings(args.home, args.ow)
        print('done.')
        
    elif args.command == 'run':
        start_server(args)
        
    else:
        print('WARNING! No command given. I guess we will just run it anyway?')
        start_server(args)


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
    print_server_startup()
#    if 'debug' not in args:
    uvicorn.run(APP_MODULE, host=HOST_IP, port=PORT, workers=WORKERS)
#    else:
#        print('Running in debug mode.')
#        uvicorn.run(APP_MODULE, host="localhost", port=PORT, reload=True)

def get_public_ip():
    print(f'The public IP address of this computer is:')
    try:
        public_ip = httpx.get('https://api.ipify.org', timeout=3).text
        print('  ->', bold_str(public_ip))
    except httpx.HTTPError as e:
        print('  ->', e)
        print('WARNING: Could not get public IP address??')

def get_other_ips():
    hostname = socket.gethostname()
    ip_list = socket.gethostbyname_ex(hostname)[-1]
    localhost = '127.0.0.1'
    if localhost in ip_list:
        ip_list.remove(localhost)
    if len(ip_list) >= 1:
        print('*** note: You have multiple IPs available:')
        for ip in ip_list:
            print('  ->',bold_str(ip))
            
def bold_str(string: str):
    return f'\033[1m{string}\033[0m'

def print_server_startup():
    print('\n( h o l o c h a t )')
    print('v', HC_VERSION, sep='', end='\n\n')
    print("~ at least it's not msockets ~", end='\n\n\n')
    print('Starting server...')
    local_ip_addr = bold_str(f'localhost:{PORT}')
    print(f'holochat will run locally at {local_ip_addr}')
    get_public_ip()
    get_other_ips()