import argparse
import json
from pathlib import Path

from pydantic import BaseModel


SETTINGS_FNAME = 'holochat_settings.json'
SCHEMA_FNAME = 'holochat_settings_schema.json'
USER_JSON_PATH = Path(Path.home(), SETTINGS_FNAME)
REPO_JSON_PATH = Path(Path(__file__).parent.parent, SETTINGS_FNAME)
SCHEMA_PATH = Path(Path(__file__).parent.parent, SCHEMA_FNAME)


class _ServerSettings(BaseModel):
    port: int = 8000
    ip: str = '0.0.0.0'
    workers: int = 2
    
class MainSettings(BaseModel):
    message_stale_secs: int | float = 10
    message_expire_secs: int | float = 60
    server: _ServerSettings = _ServerSettings()    
    settings_file: str = '<pydantic>'


def load_settings() -> MainSettings:
    """
    Autoload settings from the user's home directory or the source directory. If neither are
    found, return the default settings. Priority is given to the user's home directory. Returns
    settings as a pydantic model.
    """
    if USER_JSON_PATH.exists():
        settings = _load_settings_file(USER_JSON_PATH)
    elif REPO_JSON_PATH.exists():
        settings = _load_settings_file(REPO_JSON_PATH)
    else:
        settings = MainSettings()
    return settings


def generate_schema(save_path: str | Path, overwrite: bool = False):
    """Generate a JSON schema for the main settings model."""
    save_path = _prepare_save(save_path, overwrite)    
    defaults = MainSettings(settings_file=save_path.as_posix())
    schema = defaults.model_json_schema()
    with open(save_path, 'w') as f:
        json.dump(schema, f, indent=4)
    print('Schema saved to', save_path.as_posix())

def generate_settings(save_path: str | Path, overwrite: bool = False, with_schema: bool = True):
    """Generate a JSON config file for the main settings model."""
    save_path = _prepare_save(save_path, overwrite)
    defaults = MainSettings(settings_file=save_path.as_posix())
    if with_schema:
        config = {"$schema": SCHEMA_PATH.as_posix(), **defaults.model_dump()}
    else:
        config = defaults.model_dump()
    with open(save_path, 'w') as f:
        json.dump(config, f, indent=4)
    print('Settings saved to', save_path.as_posix())

def _prepare_save(save_path: str | Path, overwrite: bool):
    save_path = Path(save_path)
    if save_path.exists() and not overwrite:
        raise FileExistsError(f'File {save_path.as_posix()} already exists. Use --ow to overwrite.')
    return save_path

def _load_settings_file(config_path: str | Path) -> MainSettings:
    config_path = Path(config_path)
    with open(config_path, 'r') as f:
        config = json.load(f)
    settings = MainSettings(**config)
    return settings

        
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--home', action='store_true', help="Also save to user's home directory.")
    p.add_argument('--ow', action='store_true', help="Overwrite existing file(s).")
    args = p.parse_args()
    
    if args.home:
        print('Generating settings file at user home...')
        generate_settings(USER_JSON_PATH, overwrite=args.ow, with_schema=False)
        
    else:
        print('Generating schema and settings file in repo...')
        generate_schema(SCHEMA_PATH, overwrite=args.ow)
        generate_settings(REPO_JSON_PATH, overwrite=args.ow, with_schema=True)
    
    print('Done.')