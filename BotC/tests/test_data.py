""" Tests for data integrity and fetching """

import os
import pytest

from data import characters, jinxes, load_yaml, write_yaml
from urllib.parse import urlparse


EXPECTED_COUNTS = {
    "demon": 19,
    "fabled": 14,
    "loric": 9,
    "minion": 27,
    "outsider": 23,
    "townsfolk": 69,
}

# Define schema for characters
EXPECTED_CHAR_STRUCTURE = {
    # Required
    # ID and team validated by key
    "ability": {
        "required": True,
        "type": (str,),
        "max_strlen": 250,
        "min_strlen": 1,
    },
    "image": {
        "required": True,
        "validation": "URI",
        "type": (str, list),
        "max_arraylen": 3,
        "min_arraylen": 0,
        # Both arbitrarily chosen
        "max_strlen": 250,
        "min_strlen": 0,
        # Apply same logic to list items
        "items": {
            "type": (str,),
            "validation": "URI",
            "max_strlen": 250,
            "min_strlen": 0,
        }
    },
    "name": {
        "required": True,
        "type": (str,),
        "max_strlen": 50,
        "min_strlen": 1,
    },
    # Optional
    "edition": {
        "type": (str,),
        "max_strlen": 50,
        "min_strlen": 0,
    },
    "firstNight": {
        "type": (int,),
        # Arbitrarily chosen
        "max_val": 500,
        "min_val": 0,
    },
    "firstNightReminder": {
        "type": (str,),
        "max_strlen": 500,
        "min_strlen": 0,
    },
    "flavor": {
        "type": (str,),
        "max_strlen": 500,
        "min_strlen": 0,
    },
    "reminders": {
        "type": (list,),
        "max_arraylen": 20,
        "min_arraylen": 0,
        "items": {
            "type": (str,),
            "max_strlen": 30,
            "min_strlen": 0,
        },
    },
    "remindersGlobal": {
        "type": (list,),
        "max_arraylen": 20,
        "min_arraylen": 0,
        "items": {
            "type": (str,),
            "max_strlen": 25,
            "min_strlen": 0,
        },
    },
    "otherNight": {
        "type": (int,),
        # Arbitrarily chosen
        "max_val": 500,
        "min_val": 0,
    },
    "otherNightReminder": {
        "type": (str,),
        "max_strlen": 500,
        "min_strlen": 0,
    },
    "setup": {
        "type": (bool,),
    },
    "special": {
        "type": (list,),
        # Arbitrarily chosen
        "max_arraylen": 10,
        "min_arraylen": 0,
        # Item validation ignored for now
    },
}

# Some sample characters
EXPECTED_CHARACTERS = {
    "acrobat": {
        "ability": "Each night*, choose a player: if they are or become drunk or poisoned " +
                   "tonight, you die.\n",
        "edition": "carousel",
        "image": [
            "https://script.bloodontheclocktower.com/src/assets/icons/carousel/acrobat_g.webp",
            "https://script.bloodontheclocktower.com/src/assets/icons/carousel/acrobat_e.webp",
        ],
        "name": "Acrobat",
        "otherNight": 14,
        "otherNightReminder": "The Acrobat chooses a player.\n",
        "team": "townsfolk",
    },
    "pithag": {
        "ability": "Each night*, choose a player & a character they become (if not in play). If " +
                   "a Demon is made, deaths tonight are arbitrary.\n",
        "edition": "sects and violets",
        "image": [
            "https://script.bloodontheclocktower.com/src/assets/icons/snv/pithag_e.webp",
            "https://script.bloodontheclocktower.com/src/assets/icons/snv/pithag_g.webp",
        ],
        "name": "Pit-Hag",
        "otherNight": 21,
        "otherNightReminder": "The Pit-Hag chooses a player & a character. If they chose a " +
                              "character that is not in play: Put the Pit-Hag to sleep. Wake the " +
                              "target. Show the {YOU ARE} token & their new character token.\n",
        "team": "minion",
    }
}

EXPECTED_NUM_JINXES = 56

# Some sample jinxes
EXPECTED_JINXES = {
    'alhadikhia': {
        'mastermind': 'If the Al-Hadikhia dies by execution, and the Mastermind is alive, the ' +
                      'Al-Hadikhia chooses 3 good players tonight: if all 3 choose to live, evil ' +
                      'wins. Otherwise, good wins.\n',
        'princess': 'If the Princess nominated & executed a player on their 1st day, no one dies ' +
                    'to the Al-Hadikhia ability tonight.\n',
        'scarletwoman': 'If there are two living Al-Hadikhias, the Scarlet Woman Al-Hadikhia ' +
                        'becomes the Scarlet Woman again.\n',
    },
}


def _validate_as_URI(string):
    try:
        result = urlparse(string)
        if result.scheme and result.netloc:
            return
    except ValueError:
        assert False, f"{string} is not a valid URI"


def _validate_as_char_ID(string):
    assert isinstance(string, str)
    assert string.isalnum()
    assert string.lower() == string
    assert len(string) <= 50


def _validate_against_rules(item, rules):
    """Check that item matches the constraints laid out in rules"""
    assert isinstance(item, rules["type"])
    match item:
        case int():
            assert rules["min_val"] <= item
            assert rules["max_val"] >= item
        case str():
            assert rules["min_strlen"] <= len(item)
            assert rules["max_strlen"] >= len(item)
            if "validation" in rules.keys() and rules["validation"] == "URI":
                _validate_as_URI(item)
        case list():
            assert rules["min_arraylen"] <= len(item)
            assert rules["max_arraylen"] >= len(item)
            # Validate items in the list
            if "items" in rules.keys():
                for subitem in item:
                    _validate_against_rules(subitem, rules["items"])


class TestDataIntegrity():
    """Validate the data from the data subdirectory"""
    def test_team_counts(self):
        assert characters is not None
        assert isinstance(characters, dict)

        # Check all expected are present
        for team in EXPECTED_COUNTS.keys():
            assert team in characters.keys()
            assert len(characters[team]) == EXPECTED_COUNTS[team]

    def _test_character_structure(self, char_id, char):
        """
        A given character must have each of the following attributes:
        - ability : string
        - id (as the key) : string
        - image : string (URL) OR array <string>
        - name : string
        - team (as the key's parent) : string
        Note that this is more strict than the schema because this serves as a
        data source, so all characters are required to have an image.

        It may optionally include:
        - edition : string
        - firstNight and/or otherNight : int
        - firstNightReminder and/or otherNightReminder : string
        - flavor : string
        - reminders : array <string>
        - remindersGlobal : array <string>
        - setup : bool
        - special : array <dict>
        """
        _validate_as_char_ID(char_id)

        for field, rules in EXPECTED_CHAR_STRUCTURE.items():
            if "required" in rules.keys() and rules["required"]:
                assert field in char.keys()
            elif field not in char.keys():
                continue
            _validate_against_rules(char[field], rules)

    def test_team_structure(self):
        for team_id, team in characters.items():
            # Check all present are expected
            assert team_id in EXPECTED_COUNTS.keys()
            for char_id, char in team.items():
                self._test_character_structure(char_id, char)

    @pytest.mark.parametrize("char_id,char", EXPECTED_CHARACTERS.items())
    def test_sample_character(self, char_id, char):
        assert char["team"] in characters.keys()
        assert char_id in characters[char["team"]].keys()

        found = characters[char["team"]][char_id]
        for field, expected in char.items():
            if field == "team":
                # Already tested
                continue
            assert found[field] == expected

    def test_jinxes_structure(self):
        assert jinxes is not None
        assert isinstance(jinxes, dict)

        # Check all jinxes have loaded
        assert len(jinxes) == EXPECTED_NUM_JINXES

        for char1, value in jinxes.items():
            _validate_as_char_ID(char1)
            assert isinstance(value, dict)
            for char2, jinx in value.items():
                _validate_as_char_ID(char2)
                assert isinstance(jinx, str)
                assert len(jinx) <= 500

    @pytest.mark.parametrize("char,jinx_set", EXPECTED_JINXES.items())
    def test_sample_jinx(self, char, jinx_set):
        assert char in jinxes.keys()
        for char2, jinx in jinx_set.items():
            assert char2 in jinxes[char].keys()
            assert jinx == jinxes[char][char2]

    def test_order_structure(self):
        NIGHTS = ["firstNight", "otherNight"]
        order = load_yaml("./data/night-order.yaml")
        assert set(NIGHTS) == set(order.keys())
        for night in NIGHTS:
            for obj in order[night]:
                count = 0
                for char, reminder in obj.items():
                    assert count == 0
                    count += 1

                    _validate_as_char_ID(char)

                    assert isinstance(reminder, str)
                    assert 500 >= len(reminder)


YAML_TEST = {
    "string": """\
test:
  data:
  - 1
  - 2
  - fizz
  - 4
  - buzz
  name: fizzbuzz
""",
    "object": {
        "test": {
            "data": [1, 2, "fizz", 4, "buzz"],
            "name": "fizzbuzz",
        }
    },
}


class TestYAMLOperations():
    """Test that read/write function properly"""

    TEST_YAML_FILE = "./TestYAMLOperations.yaml"

    def _assert_file_matches(self, string):
        """Assert the file contents match the string"""
        with open(self.TEST_YAML_FILE, "r") as file:
            assert string == file.read()

    def test_yaml_read(self):
        try:
            # Setup
            with open(self.TEST_YAML_FILE, "w") as file:
                file.write(YAML_TEST["string"])
            # Check it worked
            self._assert_file_matches(YAML_TEST["string"])

            # Test read
            assert load_yaml(self.TEST_YAML_FILE) == YAML_TEST["object"]

        finally:
            # Cleanup
            os.remove(self.TEST_YAML_FILE)

    def test_yaml_write(self):
        try:
            write_yaml(self.TEST_YAML_FILE, YAML_TEST["object"])

            with open(self.TEST_YAML_FILE, "r") as file:
                assert file.read() == YAML_TEST["string"]

        finally:
            # Cleanup
            os.remove(self.TEST_YAML_FILE)

    def test_yaml_write_and_read(self):
        try:
            write_yaml(self.TEST_YAML_FILE, YAML_TEST["object"])
            assert load_yaml(self.TEST_YAML_FILE) == YAML_TEST["object"]
        finally:
            # Cleanup
            os.remove(self.TEST_YAML_FILE)
