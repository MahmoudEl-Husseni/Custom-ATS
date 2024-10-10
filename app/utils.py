import json

def load_config(cfg_file : str) -> dict:
    '''
    Load the configuration file
    '''
    with open(cfg_file, 'r') as f:
        cfg = json.load(f)
    return cfg
