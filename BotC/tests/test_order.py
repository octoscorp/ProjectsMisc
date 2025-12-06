""" Tests for night ordering"""

from order import pick_from_order

TB_CHARS = [
    # Town
    "chef",
    "empath",
    "fortune teller",
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
    "scarlet woman",
    "spy",
    # Demons
    "imp",
]

TB_DEFAULT_ORDER = {
    "firstNight": [
        "dusk",
        "minion info",
        "demon info",
        "poisoner",
        "washerwoman",
        "librarian",
        "investigator",
        "chef",
        "empath",
        "fortune teller",
        "butler",
        "spy",
        "dawn",
    ],
    "otherNight": [
        "dusk",
        "poisoner",
        "monk",
        "scarlet woman",
        "imp",
        "ravenkeeper",
        "empath",
        "fortune teller",
        "undertaker",
        "butler",
        "spy",
        "dawn",
    ],
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
    def test_tb_default_order(self):
        chars = TB_CHARS
        expected_order = TB_DEFAULT_ORDER

        given_order = pick_from_order(chars)
        _assert_matching_order(given_order, expected_order)
