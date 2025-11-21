"""
Script to generate/fetch a night ordering of all characters. Can be run
independently to generate the night order with user input, or imported to use
the data.
"""
from data import characters, write_yaml


_NIGHT_ORDER_FILE = './data/night-order.yaml'


class _Orderable:
    """Defines a less-than function to allow sorting"""
    def __init__(self, name, reminder_text):
        self.name = name
        self.reminder_text = reminder_text

    def __lt__(self, other):
        """Compare with another character"""
        return input(f"Should {self.name} go before {other.name}? [y/N] ") \
               .lower().strip() == 'y'

    def output(self):
        """YAML-compatible output format"""
        return {self.name: self.reminder_text}


def generate_order():
    # Define dawn/dusk for consistency
    _DUSK = _Orderable("dusk", "Start the Night Phase.")
    _DAWN = _Orderable("dawn", \
                                "Wait for a few seconds. End the Night Phase.")

    # Load all characters
    all_chars = characters["townsfolk"] | characters["outsiders"] | \
                characters["minions"] | characters["demons"]
    order = {
        "first night": [_DAWN],
        "other nights": [_DAWN],
    }

    for char_name in all_chars.keys():
        # Determine whether character wakes at night
        if "reminders" not in all_chars[char_name].keys():
            continue
        reminders = all_chars[char_name]["reminders"]
        for night in order.keys():
            if night in reminders.keys():
                orderable = _Orderable(char_name, reminders[night])
                order[night].append(orderable)

    # Sort into correct order (where each comparison asks the user)
    for night in order.keys():
        print(f"== {night} ============")
        order[night].sort()
        order[night] = [_DUSK.output()] + \
                       [char.output() for char in order[night]]

    # Write to file
    write_yaml(_NIGHT_ORDER_FILE, order)


if __name__ == '__main__':
    generate_order()