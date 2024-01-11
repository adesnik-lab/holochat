import argparse
import json
from pathlib import Path

from pydantic import BaseModel


class _ServerSettings(BaseModel):
    port: int = 8000
    ip: str = '0.0.0.0'
    workers: int = 2
    
class MainSettings(BaseModel):
    message_stale_secs: int | float = 10
    message_expire_secs: int | float = 60
    server: _ServerSettings = _ServerSettings()    


def generate_schema(save_path: str | Path, overwrite: bool = False):
    """Generate a JSON schema for the main settings model."""
    save_path = _prepare_save(save_path, overwrite)    
    defaults = MainSettings()
    schema = defaults.model_json_schema()
    with open(save_path, 'w') as f:
        json.dump(schema, f, indent=4)
    print('Schema saved to', save_path.as_posix())

def generate_config(save_path: str | Path, overwrite: bool = False, with_schema: bool = True):
    """Generate a JSON config file for the main settings model."""
    save_path = _prepare_save(save_path, overwrite)
    defaults = MainSettings()
    if with_schema:
        config = {"$schema": "./settings_schema.json", **defaults.model_dump()}
    else:
        config = defaults.model_dump()
    with open(save_path, 'w') as f:
        json.dump(config, f, indent=4)
    print('Config saved to', save_path.as_posix())
    
def _prepare_save(save_path: str | Path, overwrite: bool):
    save_path = Path(save_path)
    if save_path.exists() and not overwrite:
        raise FileExistsError(f'File {save_path.as_posix()} already exists.')
    return save_path

def load_settings_file(config_path: str | Path) -> MainSettings:
    """Load settings from a JSON config file."""
    config_path = Path(config_path)
    with open(config_path, 'r') as f:
        config = json.load(f)
    settings = MainSettings(**config)
    return settings

def load_settings(config_path: str | Path) -> MainSettings:
    """Load settings from a JSON config file."""
    config_path = Path(config_path)
    # if there is a config file, load it
    if config_path.exists():
        settings = load_settings_file(config_path)
    # otherwise create from defaults
    else:
        settings = MainSettings()
    return settings
        
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--schema', action='store_true')
    p.add_argument('--ow', action='store_true')
    args = p.parse_args()
    
    if args.schema:
        print('Generating schema and config files...')
        generate_schema('settings_schema.json', overwrite=args.ow)
        generate_config('config.json', overwrite=args.ow, with_schema=True)
    else:
        print('Generating config file...')
        generate_config('config.json', overwrite=args.ow, with_schema=False)
    print('Done.')