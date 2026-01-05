"""
Parser to process the YAML data stored in the ./data directory.
Also has facility to write

Grab as needed i.e.:

from data import characters
"""
import yaml


def load_yaml(filename):
    try:
        with open(filename, 'r') as file:
            file_data = yaml.safe_load(file)
            return file_data
    except FileNotFoundError:
        print(f"Could not find {filename}")
    except yaml.YAMLError as e:
        print(f"Error parsing yaml from {filename}: {e}")
    return None


def write_yaml(filename, contents):
    with open(filename, 'w') as file:
        yaml.dump(contents, file, default_flow_style=False)


# === Exports ===
characters = load_yaml('./data/characters.yaml')
jinxes = load_yaml('./data/jinxes.yaml')
