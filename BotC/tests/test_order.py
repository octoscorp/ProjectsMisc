""" Tests for night ordering"""

import pytest

from order import pick_from_order

TEST_DATA = {
    "tb": {
        "chars": [
            # Town
            "chef",
            "empath",
            "fortuneteller",
            "investigator",
            "librarian",
            "mayor",
            "monk",
            "ravenkeeper",
            "slayer",
            "soldier",
            "undertaker",
            "virgin",
            "washerwoman",
            # Outsiders
            "butler",
            "drunk",
            "recluse",
            "saint",
            # Minions
            "baron",
            "poisoner",
            "scarletwoman",
            "spy",
            # Demons
            "imp",
        ],
        "expected_order": {
            # Not actually the order of the script, because they modify it away from the default
            "firstNight": [
                "dusk",
                "minioninfo",
                "demoninfo",
                "poisoner",
                "washerwoman",
                "librarian",
                "investigator",
                "chef",
                "empath",
                "fortuneteller",
                "butler",
                "spy",
                "dawn",
            ],
            "otherNight": [
                "dusk",
                "poisoner",
                "monk",
                "scarletwoman",
                "imp",
                "ravenkeeper",
                "empath",
                "fortuneteller",
                "undertaker",
                "butler",
                "spy",
                "dawn",
            ],
        }
    },
    "snv": {
        "chars": [
            # Town
            "clockmaker",
            "dreamer",
            "snakecharmer",
            "mathematician",
            "flowergirl",
            "towncrier",
            "oracle",
            "savant",
            "seamstress",
            "philosopher",
            "artist",
            "juggler",
            "sage",
            # Outsiders
            "mutant",
            "sweetheart",
            "barber",
            "klutz",
            # Minions
            "eviltwin",
            "witch",
            "cerenovus",
            "pithag",
            # Demons
            "fanggu",
            "vigormortis",
            "nodashii",
            "vortox",
        ],
        "expected_order": {
            "firstNight": [
                "dusk",
                "philosopher",
                "minioninfo",
                "demoninfo",
                "snakecharmer",
                "eviltwin",
                "witch",
                "cerenovus",
                "clockmaker",
                "dreamer",
                "seamstress",
                "mathematician",
                "dawn",
            ],
            "otherNight": [
                "dusk",
                "philosopher",
                "snakecharmer",
                "witch",
                "cerenovus",
                "pithag",
                "fanggu",
                "nodashii",
                "vortox",
                "vigormortis",
                "barber",
                "sweetheart",
                "sage",
                "dreamer",
                "flowergirl",
                "towncrier",
                "oracle",
                "seamstress",
                "juggler",
                "mathematician",
                "dawn",
            ],
        }
    }
}


def _assert_matching_order(given_order, expected_order):
    """
    Compares the content-rich given order with the test list format
    @param given_order output of an ordering - dict of format:
    {
        "firstNight": [
            {<name>: <first_night_reminder>},
            ...
        ],
        "otherNight": [
            {<name>: <other nights_reminder>},
            ...
        ]
    }
    @param expected_order list of night order with reminder names
    """
    for night in given_order.keys():
        # Just in case
        assert night in expected_order.keys()
        # Check they're in the same order
        count = 0
        for char_object in given_order[night]:
            names = list(char_object.keys())
            # No double-naming weirdness!
            assert 1 == len(names)
            assert names[0] == expected_order[night][count]
            count += 1
        # Make sure none were left off
        assert count == len(expected_order[night])


class TestPickFromOrder():
    """Tests of the pick_from_order function"""
    @pytest.mark.parametrize("script", TEST_DATA.keys())
    def test_pick_from_order(self, script):
        chars = TEST_DATA[script]["chars"]
        expected_order = TEST_DATA[script]["expected_order"]

        given_order = pick_from_order(chars)
        _assert_matching_order(given_order, expected_order)
