"""
For generating a script with the maximum number of Jinxes.
"""
import signal

from data import characters, jinxes

from datetime import datetime
from itertools import combinations


TOWN_DISTRIBUTION = {
    "townsfolk": 13,
    "outsiders": 4,
    "minions": 4,
    "demons": 4,
}


start_time = 0
checked_solns = 0
last_soln = []
last_interrupt = datetime.now()


def dict_member_append(dictionary, key, value):
    """Append to a list which is a member of a dict. If it doesn't exist, create the list"""
    if dictionary.get(key) is None:
        dictionary[key] = []
    dictionary[key].append(value)


def sigint_handler(_signum, _frame):
    """Update on status. Should be SIGINFO, but no library support"""
    global last_interrupt
    curr_time = datetime.now()
    elapsed_time = curr_time - start_time
    print(f'SIGINT: checked {checked_solns} in {elapsed_time}s. Last seen:\n  {last_soln}')
    if (curr_time - last_interrupt).total_seconds() < 5:
        raise KeyboardInterrupt("")
    last_interrupt = curr_time


class _JinxGraph():
    def __init__(self, jinx_dict):
        """
        Create a new JinxGraph.
        @param jinx_dict dictionary of jinxes in format:
        {
            <char_name>: {
                <jinxed_char_name>: <jinx_description>,
                ...
            }, ...
        }
        NOTE: It is assumed that jinx_dict stores jinxes such that <char_name> is alphabetically
          before <jinxed_char_name>. Otherwise, get_num_jinxes will not work. This is because the
          adjacency list does not currently create reverse adjacencies. (The other order is allowed
          to be present, but will not be used.)
        """
        # Create adjacency list
        self.adj_list = {}
        for char_name in jinx_dict.keys():
            for jinxed_char_name in jinx_dict[char_name].keys():
                dict_member_append(self.adj_list, char_name, jinxed_char_name)

    def get_num_jinxes(self, char_list):
        """
        Returns number of jinxes obtained by having the character set in play.
        Uses the fact that jinxes are stored under the character which is first alphabetically.
        """
        count = 0
        search_space = char_list[:]
        # Remove unjinxed characters
        for i in range(len(search_space) - 1, -1, -1):
            if self.adj_list.get(search_space[i]) is None:
                del search_space[i]

        # Sort alphabetically (half adjacency list)
        search_space = sorted(search_space)

        # For each remaining character, only check the characters after it in the list
        for i in range(len(search_space)):
            char_name = search_space[i]
            for j in range(i + 1, len(search_space)):
                jinxed_char_name = search_space[j]
                if jinxed_char_name in self.adj_list[char_name]:
                    count += 1
        return count


def exhaustion_search(graph):
    """
    Cleverer search solutions exist, however I want to be sure I haven't missed anything
    """
    global checked_solns, last_soln

    max_jinxes = 0
    optimal_solutions = []
    # Try every combination!
    for townsfolk in combinations(characters["townsfolk"].keys(),
                                       TOWN_DISTRIBUTION["townsfolk"]):
        for outsiders in combinations(characters["outsiders"].keys(),
                                           TOWN_DISTRIBUTION["outsiders"]):
            for minions in combinations(characters["minions"].keys(),
                                            TOWN_DISTRIBUTION["minions"]):
                for demons in combinations(characters["demons"].keys(),
                                                TOWN_DISTRIBUTION["demons"]):
                    chars = list(townsfolk + outsiders + minions + demons)
                    # The magic check
                    num_jinxes = graph.get_num_jinxes(chars)
                    if num_jinxes > max_jinxes:
                        max_jinxes = num_jinxes
                        optimal_solutions = []
                    if num_jinxes == max_jinxes:
                        optimal_solutions.append(chars)

                    # Update for SIGINFO
                    checked_solns += 1
                    last_soln = chars
    return optimal_solutions


def output_scripts(solutions):
    """
    TODO: Write to script file
    """
    print(solutions)


def main():
    global start_time
    graph = _JinxGraph(jinxes)

    signal.signal(signal.SIGINT, sigint_handler)
    start_time = datetime.now()

    solutions = exhaustion_search(graph)

    elapsed_time = datetime.now() - start_time
    print(f"Took {elapsed_time} seconds to complete")

    output_scripts(solutions)


if __name__ == "__main__":
    main()
