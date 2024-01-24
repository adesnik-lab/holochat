import json
from pathlib import Path

import pytest

from holochat.settings import (MainSettings, generate_schema,
                               generate_settings, load_settings, save_settings,
                               USER_JSON_PATH, REPO_JSON_PATH)


@pytest.fixture
def settings_path(tmp_path: Path):
    return Path(tmp_path, 'test_settings.json')

@pytest.fixture
def schema_path(tmp_path: Path):
    return Path(tmp_path, 'test_schema.json')


def test_load_settings_type():
    settings = load_settings()
    assert isinstance(settings, MainSettings)
    
def test_generate_new_schema(schema_path: Path):
    generate_schema(schema_path, overwrite=False)
    assert Path(schema_path).exists()
    
def test_generate_new_settings(settings_path: Path):
    generate_settings(settings_path, overwrite=False)
    assert Path(settings_path).exists()
    
def test_settings_file_exists(settings_path: Path):
    generate_settings(settings_path, overwrite=False)
    with pytest.raises(FileExistsError):
        generate_settings(settings_path, overwrite=False)

def test_generate_schema_with_overwrite(schema_path: Path):
    generate_schema(schema_path, overwrite=True)
    try:
        generate_schema(schema_path, overwrite=True)
    except Exception as e:
        assert False, f"generate_schema raised an exception: {e}"
    generate_schema(schema_path, overwrite=True)
    assert Path(schema_path).exists()

def test_generate_settings_with_schema(schema_path: Path):
    generate_settings(schema_path, overwrite=False, with_schema=True)
    assert Path(schema_path).exists()
    assert "$schema" in json.load(open(schema_path))

def test_generate_settings_without_schema(settings_path: Path):
    generate_settings(settings_path, overwrite=False, with_schema=False)
    assert Path(settings_path).exists()
    assert "$schema" not in json.load(open(settings_path))
    
def test_nofiles_load_pydantic(fs):
    settings = load_settings()
    assert '<pydantic>' in settings.settings_file
    
def test_loads_from_user_home(fs):
    fs.create_dir(USER_JSON_PATH.parent)
    generate_settings(USER_JSON_PATH, overwrite=False)
    settings = load_settings()
    assert settings.settings_file == USER_JSON_PATH.as_posix()
    
def test_loads_from_repo(fs):
    fs.create_dir(REPO_JSON_PATH.parent)
    generate_settings(REPO_JSON_PATH, overwrite=False)
    settings = load_settings()
    assert settings.settings_file == REPO_JSON_PATH.as_posix()
    
def test_loads_user_has_priority(fs):
    fs.create_dir(USER_JSON_PATH.parent)
    fs.create_dir(REPO_JSON_PATH.parent)
    generate_settings(USER_JSON_PATH, overwrite=False)
    generate_settings(REPO_JSON_PATH, overwrite=False)
    settings = load_settings()
    assert settings.settings_file == USER_JSON_PATH.as_posix()
    
def test_save_settings_at_home():
    save_settings(use_home=True, overwrite=False)
    assert USER_JSON_PATH.exists()
    
def test_save_settings_at_repo():
    save_settings(use_home=False, overwrite=False)
    assert REPO_JSON_PATH.exists()