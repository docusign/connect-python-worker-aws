import configparser
import itertools
import os

def ds_config(str):
    config = {}
    client_id = os.environ.get('DS_CLIENT_ID', None)
    if client_id is not None:
        config[str] = os.environ.get(str)
    else:
        ini_file = 'ds_config.ini'
        if os.path.isfile(ini_file):
            config_parser = configparser.ConfigParser()
            with open(ini_file) as fp:
                # Enable ini file to not have explicit global section
                config_parser.read_file(itertools.chain(['[global]'], fp), source=ini_file)
            config = config_parser['global']
        else:
            raise Exception(f"Missing config file |{ini_file}| and environment variables are not set.")
    return config[str]

def aud():
    auth_server = ds_config("DS_AUTH_SERVER")
    if 'https://' in auth_server:
        aud = auth_server[8:]
    else: # assuming http://blah
        aud = auth_server[7:]
    return aud

def api():
    return "restapi/v2"

def permission_scopes():
    return "signature impersonation"

def jwt_scope():
    return "signature"