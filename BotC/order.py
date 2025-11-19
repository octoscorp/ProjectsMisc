"""
Script to generate/fetch a night ordering of all characters. Can be run
independently to generate the night order with user input, or imported to use
the data.
"""
from data import characters, write_yaml


_NIGHT_ORDER_FILE = './data/night-order.yaml'


class _OrderableCharacter:
    """Defines a less-than function to allow sorting"""
    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        """Compare with another character"""
        return input(f"Should {self.name} go before {other.name}? [y/N] ").lower().strip() == 'y'


def generate_order():
    # Load all characters
    all_chars = characters["townsfolk"] | characters["outsiders"] | characters["minions"] | characters["demons"]
    order = {
        "night 1": [],
        "other nights": [],
    }

    for char_name in all_chars.keys():
        # Determine whether character wakes at night
        wakes_1 = input(f"Does {char_name} wake night 1? [y/N] ").lower().strip() == 'y'
        wakes_other = input(f"Does {char_name} wake on other nights? [y/N] ").lower().strip() == 'y'
        if wakes_1:
            order["night 1"].append(_OrderableCharacter(char_name))
        if wakes_other:
            order["other nights"].append(_OrderableCharacter(char_name))

    print("== Night 1 ============")
    # Sort into correct order (where each comparison asks the user), then simplify
    order["night 1"].sort()
    order["night 1"] = [char.name for char in order["night 1"]]

    print("== Other Nights =======")
    order["other nights"].sort()
    order["other nights"] = [char.name for char in order["other nights"]]

    # Write to file
    write_yaml(_NIGHT_ORDER_FILE, order)


if __name__ == '__main__':
    generate_order()