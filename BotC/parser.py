"""
Parser to process the YAML data stored in the ./data directory.

Grab as needed i.e.:

from parser import characters
"""

import yaml

characters = YAMLFile('./data/characters.yaml')

class YAMLFile():
    def __init__(self, filename):
        pass


def test_characters():
    assert characters != None
    assert characters is YAMLFile
    
    # Check all data has loaded
    # assert characters.count("townsfolk") == 69
    # assert characters.count("outsiders") == 23
    # assert characters.count("minions") == 27
    # assert characters.count("demons") == 19

    # Check arbitrary sub-attributes


if __name__ == "__main__":
    test_characters()