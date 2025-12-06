"""
Script to generate/fetch a night ordering of characters. Can be run independently to generate the
night order with user input, or imported to use the data.
"""
from data import characters, write_yaml, load_yaml


_DEFAULT_NIGHT_ORDER_FILE = './data/night-order.yaml'


class _Orderable:
    """Defines a less-than function to allow sorting"""
    def __init__(self, name, reminder_text):
        self.name = name
        self.reminder_text = reminder_text

    def __lt__(self, other):
        """Compare with another character"""
        decision = input(f"Should {self.name} go before {other.name}? [y/N] ")
        return "y" == decision.lower().strip()

    def output(self):
        """YAML-compatible output format"""
        return {self.name: self.reminder_text.strip()}


def generate_order(char_set, filename=None):
    """
    Generate night order for characters specified in char_set. If filename is not None, write output
    in YAML format to the specified file.
    @param char_set dict of characters in the following format:
    {
        <name>: {
            ["firstNight": <first night reminder>,]
            ["otherNight": <other nights reminder>]
        }, ...
    }
    @param filename the file to write results to when done. Will silently overwrite if this exists!
    @return order dict of night order in the below format. This includes dusk and dawn
    {
        "firstNight": [
            {<name>: <first night reminder>},
            ...
        ],
        "otherNight": [
            {<name>: <other nights reminder>},
            ...
        ]
    }
    """
    # Define dawn/dusk for consistency
    _DUSK = _Orderable("dusk", "Start the Night Phase.")
    _DAWN = _Orderable("dawn", "Wait for a few seconds. End the Night Phase.")
    _MINION_INFO = _Orderable("minion info",
                              "If there are 7 or more players, wake all Minions: Show the {THIS " +
                              "IS THE DEMON} token. Point to the Demon. Show the {THESE ARE YOUR " +
                              "MINIONS} token. Point to the other Minions.")
    _DEMON_INFO = _Orderable("demon info",
                             "If there are 7 or more players, wake the Demon: Show the {THESE " +
                             "ARE YOUR MINIONS} token. Point to all Minions. Show the {THESE " +
                             "CHARACTERS ARE NOT IN PLAY} token. Show 3 not-in-play good " +
                             "character tokens.")
    order = {
        "firstNight": [_DAWN, _MINION_INFO, _DEMON_INFO],
        "otherNight": [_DAWN],
    }

    for char_name in char_set.keys():
        # Determine whether character wakes at night
        for night in order.keys():
            if night in char_set[char_name].keys() and char_set[char_name][night] != 0:
                orderable = _Orderable(char_name, char_set[char_name][night])
                order[night].append(orderable)

    # Sort into correct order (where each comparison asks the user)
    for night in order.keys():
        print(f"== {night} ============")
        order[night].sort()
        order[night] = [_DUSK.output()] + \
                       [char.output() for char in order[night]]

    # Write to file
    if filename is not None:
        write_yaml(filename, order)
    return order


def pick_from_order(character_names, filename=_DEFAULT_NIGHT_ORDER_FILE):
    """
    Assign characters a night order from the specified file.
    @param character_names list of character names to include in the order
    @param filename save file to source order from (defaults to ./data/night-order.yaml)
    @return order dict of night order in the below format. This includes dusk and dawn
    {
        "first night": [
            {<name>: <first night reminder>},
            ...
        ],
        "other nights": [
            {<name>: <other nights reminder>},
            ...
        ]
    }
    """
    order = load_yaml(filename)

    names_to_keep = character_names + ["dusk", "dawn", "minion info", "demon info"]

    try:
        for night in order.keys():
            to_remove = []
            for i in range(len(order[night])):
                char_object = order[night][i]
                char_name = list(char_object.keys())[0]
                if char_name not in names_to_keep:
                    to_remove.append(i)
            # Remove later because list traversal funtimes
            for i in reversed(to_remove):
                del order[night][i]
        return order
    except ValueError as e:
        raise ValueError(f"Issue while processing data from {filename}: {e.msg}")


# If run directly, generate ./data/night-order.yaml
if __name__ == '__main__':
    # Load all characters
    all_chars = characters["townsfolk"] | characters["outsider"] | \
                characters["minion"] | characters["demon"]
    generate_order(all_chars, _DEFAULT_NIGHT_ORDER_FILE)
