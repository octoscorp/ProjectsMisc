"""
Parser to process the YAML data stored in the ./data directory.

Grab as needed i.e.:

from parser import characters
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

# === Exports ===
characters = load_yaml('./data/characters.yaml')
jinxes = load_yaml('./data/jinxes.yaml')

def test_characters():
    assert characters != None
    assert isinstance(characters, dict)
    
    # Check all characters have loaded
    expected = {
        "townsfolk": 69,
        "outsiders": 23,
        "minions": 27,
        "demons": 19,
    }

    for category in expected.keys():
        assert category in characters.keys()
        assert len(characters[category]) == expected[category]

    # Check character structure
    expected = {
        "townsfolk": {
            "acrobat": {
                "description": "Each night*, choose a player: if they are or become drunk or poisoned tonight, you die.\n",
                "source": "carousel",
            },
        },
    }

    for category in expected.keys():
        for char_name in expected[category].keys():
            assert char_name in characters[category],keys()
            for attr in expected[category][char_name].keys():
                assert characters[category][char_name][attr] == expected[category][char_name][attr], f"{characters[category][char_name][attr]} does not match (expected) {expected[category][char_name][attr]}"


def test_jinxes():
    assert jinxes != None
    assert isinstance(jinxes, dict)

    # Check all jinxes have loaded
    assert len(jinxes) == 56

    # Check structure
    expected = {
        'al-hadikhia': {
            'mastermind': 'If the Al-Hadikhia dies by execution, and the Mastermind is alive, the Al-Hadikhia chooses 3 good players tonight: if all 3 choose to live, evil wins. Otherwise, good wins.\n',
            'princess': 'If the Princess nominated & executed a player on their 1st day, no one dies to the Al-Hadikhia ability tonight.\n',
            'scarlet woman': 'If there are two living Al-Hadikhias, the Scarlet Woman Al-Hadikhia becomes the Scarlet Woman again.\n',
        },
    }

    for char_name in expected.keys():
        assert char_name in jinxes.keys()
        for jinxed_char_name in expected[char_name].keys():
            assert jinxed_char_name in jinxes[char_name].keys()
            assert jinxes[char_name][jinxed_char_name] == expected[char_name][jinxed_char_name]


if __name__ == "__main__":
    test_characters()
    test_jinxes()